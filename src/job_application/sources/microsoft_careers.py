"""Microsoft Eightfold public careers adapter with targeted search support."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, ClassVar

import httpx

from job_application.domain.models import (
    Compensation,
    DiscoveredJob,
    MicrosoftCareersSourceConfig,
    SourceKind,
)
from job_application.sources.base import JobSource
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.utils import (
    html_to_text,
    non_empty_string,
    normalize_workplace,
    parse_datetime,
    unique_strings,
)

_USD_RANGE = re.compile(
    r"USD\s*\$([\d,]+(?:\.\d+)?)\s*-\s*\$([\d,]+(?:\.\d+)?)\s+per year",
    re.IGNORECASE,
)
_BROWSER_HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
    ),
}


@dataclass(frozen=True)
class _Candidate:
    position_id: str
    title: str
    search_payload: dict[str, Any]


class MicrosoftCareersSource(JobSource[MicrosoftCareersSourceConfig]):
    """Fetch a deduplicated union from Microsoft's public Eightfold job search."""

    kind: ClassVar[SourceKind] = SourceKind.MICROSOFT_CAREERS

    async def list_jobs(self, config: MicrosoftCareersSourceConfig) -> list[DiscoveredJob]:
        base_url = config.api_base_url.rstrip("/")
        async with self.client_session() as client:
            candidates = await self._search_candidates(client, config, base_url)
            if len(candidates) > config.max_details:
                raise SourcePayloadError(
                    self.kind,
                    f"candidate set has {len(candidates)} jobs, exceeding max_details="
                    f"{config.max_details}; narrow the search or title keywords",
                )
            jobs = await self._fetch_details(client, config, base_url, candidates)

        deduplicated = {job.external_id: job for job in jobs if job is not None}
        return sorted(
            deduplicated.values(),
            key=lambda job: (job.title.casefold(), job.external_id),
        )

    async def _search_candidates(
        self,
        client: httpx.AsyncClient,
        config: MicrosoftCareersSourceConfig,
        base_url: str,
    ) -> list[_Candidate]:
        candidates: dict[str, _Candidate] = {}
        search_texts = tuple(text.strip() for text in config.search_texts if text.strip()) or ("",)

        for search_text in search_texts:
            for page_index in range(config.max_pages_per_search):
                start = page_index * config.page_size
                payload = await self.get_json(
                    client,
                    f"{base_url}/api/pcsx/search",
                    params={
                        "domain": config.domain,
                        "query": search_text,
                        "location": "",
                        "start": start,
                        "sort_by": "relevance",
                    },
                    headers=_BROWSER_HEADERS,
                )
                postings, total = self._parse_search_page(payload)
                for raw in postings:
                    position_id = non_empty_string(raw.get("id"))
                    title = non_empty_string(raw.get("name"))
                    if position_id is None or title is None:
                        raise SourcePayloadError(
                            self.kind,
                            f"search result for {search_text!r} at start={start} is missing "
                            f"id or name: {dict(raw)!r}",
                        )
                    if not self._title_is_candidate(title, config.candidate_title_keywords):
                        continue
                    candidates.setdefault(
                        position_id,
                        _Candidate(
                            position_id=position_id,
                            title=title,
                            search_payload=dict(raw),
                        ),
                    )

                if start + len(postings) >= total:
                    break
                if not postings:
                    raise SourcePayloadError(
                        self.kind,
                        f"search {search_text!r} returned an empty page before count={total}",
                    )
        return list(candidates.values())

    async def _fetch_details(
        self,
        client: httpx.AsyncClient,
        config: MicrosoftCareersSourceConfig,
        base_url: str,
        candidates: list[_Candidate],
    ) -> list[DiscoveredJob | None]:
        semaphore = asyncio.Semaphore(config.detail_concurrency)

        async def fetch(candidate: _Candidate) -> DiscoveredJob | None:
            async with semaphore:
                payload = await self.get_json(
                    client,
                    f"{base_url}/api/pcsx/position_details",
                    params={
                        "position_id": candidate.position_id,
                        "domain": config.domain,
                        "hl": "en",
                    },
                    headers={
                        **_BROWSER_HEADERS,
                        "Referer": f"{base_url}/careers/job/{candidate.position_id}",
                    },
                )
            detail = self._response_data(payload, context="position detail")
            description_html = non_empty_string(detail.get("jobDescription"))
            description_text = html_to_text(description_html)
            required_text = (config.required_description_text or "").strip().casefold()
            searchable = f"{candidate.title}\n{description_text}".casefold()
            if required_text and required_text not in searchable:
                return None
            excluded_texts = tuple(
                text.strip().casefold()
                for text in config.excluded_description_texts
                if text.strip()
            )
            if any(text in searchable for text in excluded_texts):
                return None
            return self._normalize_job(config, base_url, candidate, detail, payload)

        return list(await asyncio.gather(*(fetch(candidate) for candidate in candidates)))

    def _normalize_job(
        self,
        config: MicrosoftCareersSourceConfig,
        base_url: str,
        candidate: _Candidate,
        detail: Mapping[str, Any],
        payload: Any,
    ) -> DiscoveredJob:
        external_id = non_empty_string(
            detail.get("displayJobId") or detail.get("atsJobId") or detail.get("id")
        )
        title = non_empty_string(detail.get("name"))
        position_id = non_empty_string(detail.get("id")) or candidate.position_id
        public_url = non_empty_string(detail.get("publicUrl"))
        position_url = non_empty_string(detail.get("positionUrl"))
        job_url = public_url or (
            f"{base_url}{position_url}" if position_url else f"{base_url}/careers/job/{position_id}"
        )
        if external_id is None or title is None:
            raise SourcePayloadError(
                self.kind, "position detail is missing displayJobId/atsJobId or name"
            )

        description_html = non_empty_string(detail.get("jobDescription"))
        location_values: list[object] = [detail.get("location")]
        detail_locations = detail.get("locations")
        if isinstance(detail_locations, list):
            location_values.extend(detail_locations)
        search_locations = candidate.search_payload.get("locations")
        if isinstance(search_locations, list):
            location_values.extend(search_locations)
        locations = unique_strings(location_values)
        employment_values = detail.get("efcustomTextEmploymentType")
        employment_type = non_empty_string(
            employment_values[0]
            if isinstance(employment_values, list) and employment_values
            else None
        )
        department = non_empty_string(
            detail.get("department") or candidate.search_payload.get("department")
        )
        return DiscoveredJob(
            source=self.kind,
            source_identifier=config.domain,
            external_id=external_id,
            company_name=config.company_name,
            title=title,
            locations=locations,
            description_text=html_to_text(description_html),
            description_html=description_html,
            employment_type=employment_type,
            workplace_type=normalize_workplace(detail.get("workLocationOption")),
            departments=(department,) if department else (),
            job_url=job_url,
            apply_url=f"{base_url}/careers/apply?pid={position_id}",
            published_at=parse_datetime(detail.get("postedTs")),
            compensation=self._compensation(description_html),
            raw_payload={
                "search": candidate.search_payload,
                "detail": dict(detail),
                "response": payload,
            },
        )

    @classmethod
    def _parse_search_page(cls, payload: Any) -> tuple[list[Mapping[str, Any]], int]:
        data = cls._response_data(payload, context="search")
        postings = data.get("positions")
        total = data.get("count")
        if (
            not isinstance(postings, list)
            or isinstance(total, bool)
            or not isinstance(total, int)
            or total < 0
        ):
            raise SourcePayloadError(cls.kind, "search response has invalid positions or count")
        if any(not isinstance(item, Mapping) for item in postings):
            raise SourcePayloadError(cls.kind, "search positions contain a non-object item")
        return postings, total

    @classmethod
    def _response_data(cls, payload: Any, *, context: str) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping):
            raise SourcePayloadError(cls.kind, f"{context} response is not an object")
        status = payload.get("status")
        data = payload.get("data")
        if status != 200 or not isinstance(data, Mapping):
            raise SourcePayloadError(cls.kind, f"{context} response has invalid status or data")
        return data

    @staticmethod
    def _title_is_candidate(title: str, keywords: tuple[str, ...]) -> bool:
        normalized_keywords = tuple(
            keyword.strip().casefold() for keyword in keywords if keyword.strip()
        )
        if not normalized_keywords:
            return True
        normalized_title = title.casefold()
        return any(keyword in normalized_title for keyword in normalized_keywords)

    @staticmethod
    def _compensation(description_html: str | None) -> Compensation | None:
        ranges = _USD_RANGE.findall(html_to_text(description_html))
        if not ranges:
            return None
        minimum = min(float(low.replace(",", "")) for low, _high in ranges)
        maximum = max(float(high.replace(",", "")) for _low, high in ranges)
        return Compensation(
            summary=f"${minimum:,.0f} - ${maximum:,.0f}",
            currency="USD",
            interval="year",
            min_value=minimum,
            max_value=maximum,
            raw={"ranges": [list(value) for value in ranges]},
        )
