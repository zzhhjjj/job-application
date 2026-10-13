"""Workday public candidate-site adapter with targeted search support."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, ClassVar
from urllib.parse import quote

import httpx

from job_application.domain.models import (
    Compensation,
    DiscoveredJob,
    SourceKind,
    WorkdaySourceConfig,
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
    r"([\d,]+(?:\.\d+)?)\s+USD\s*-\s*([\d,]+(?:\.\d+)?)\s+USD",
    re.IGNORECASE,
)
_DOLLAR_RANGE = re.compile(r"\$([\d,]+(?:\.\d+)?)\s*-\s*\$([\d,]+(?:\.\d+)?)")


@dataclass(frozen=True)
class _Candidate:
    path: str
    title: str
    search_payload: dict[str, Any]


class WorkdaySource(JobSource[WorkdaySourceConfig]):
    """Fetch a deduplicated union of public Workday searches and their details."""

    kind: ClassVar[SourceKind] = SourceKind.WORKDAY

    async def list_jobs(self, config: WorkdaySourceConfig) -> list[DiscoveredJob]:
        base_url = self._base_url(config)
        async with self.client_session() as client:
            candidates = await self._search_candidates(client, config, base_url)
            if len(candidates) > config.max_details:
                raise SourcePayloadError(
                    self.kind,
                    f"candidate set has {len(candidates)} jobs, exceeding max_details="
                    f"{config.max_details}; narrow the search or title keywords",
                )
            jobs = await self._fetch_details(client, config, base_url, candidates)

        deduplicated: dict[str, DiscoveredJob] = {}
        for job in jobs:
            deduplicated.setdefault(job.external_id, job)
        return sorted(
            deduplicated.values(),
            key=lambda job: (job.title.casefold(), job.external_id),
        )

    async def _search_candidates(
        self,
        client: httpx.AsyncClient,
        config: WorkdaySourceConfig,
        base_url: str,
    ) -> list[_Candidate]:
        search_url = f"{base_url}/jobs"
        candidates: dict[str, _Candidate] = {}
        search_texts = tuple(text.strip() for text in config.search_texts if text.strip()) or ("",)

        for search_text in search_texts:
            expected_total: int | None = None
            for page_index in range(config.max_pages_per_search):
                offset = page_index * config.page_size
                payload = await self.post_json(
                    client,
                    search_url,
                    payload={
                        "appliedFacets": {},
                        "limit": config.page_size,
                        "offset": offset,
                        "searchText": search_text,
                    },
                )
                postings, total = self._parse_search_page(payload)
                if expected_total is None:
                    expected_total = total
                elif total not in {0, expected_total}:
                    raise SourcePayloadError(
                        self.kind,
                        f"result total for {search_text!r} changed from "
                        f"{expected_total} to {total}",
                    )

                for raw in postings:
                    path = non_empty_string(raw.get("externalPath"))
                    title = non_empty_string(raw.get("title"))
                    if path is None or title is None:
                        bullet_fields = raw.get("bulletFields")
                        if (
                            path is None
                            and title is None
                            and isinstance(bullet_fields, list)
                            and any(non_empty_string(value) for value in bullet_fields)
                        ):
                            # Workday occasionally leaves a requisition-only placeholder in an
                            # otherwise valid search page. There is no detail URL to retrieve.
                            continue
                        raise SourcePayloadError(
                            self.kind,
                            f"search result for {search_text!r} at offset={offset} is missing "
                            f"title or externalPath: {dict(raw)!r}",
                        )
                    if not self._title_is_candidate(title, config.candidate_title_keywords):
                        continue
                    candidates.setdefault(
                        path,
                        _Candidate(path=path, title=title, search_payload=dict(raw)),
                    )

                if offset + len(postings) >= expected_total:
                    break
                if not postings:
                    raise SourcePayloadError(
                        self.kind,
                        f"search {search_text!r} returned an empty page before total={total}",
                    )
            else:
                raise SourcePayloadError(
                    self.kind,
                    f"search {search_text!r} exceeded max_pages_per_search="
                    f"{config.max_pages_per_search}",
                )
        return list(candidates.values())

    async def _fetch_details(
        self,
        client: httpx.AsyncClient,
        config: WorkdaySourceConfig,
        base_url: str,
        candidates: list[_Candidate],
    ) -> list[DiscoveredJob]:
        semaphore = asyncio.Semaphore(config.detail_concurrency)

        async def fetch(candidate: _Candidate) -> DiscoveredJob:
            async with semaphore:
                payload = await self.get_json(client, f"{base_url}{candidate.path}")
            if not isinstance(payload, Mapping):
                raise SourcePayloadError(self.kind, "job detail is not an object")
            info = payload.get("jobPostingInfo")
            if not isinstance(info, Mapping):
                raise SourcePayloadError(self.kind, "job detail is missing jobPostingInfo")
            return self._normalize_job(config, candidate, info, payload)

        return list(await asyncio.gather(*(fetch(candidate) for candidate in candidates)))

    def _normalize_job(
        self,
        config: WorkdaySourceConfig,
        candidate: _Candidate,
        info: Mapping[str, Any],
        payload: Mapping[str, Any],
    ) -> DiscoveredJob:
        external_id = non_empty_string(info.get("jobReqId") or info.get("id"))
        title = non_empty_string(info.get("title"))
        job_url = non_empty_string(info.get("externalUrl"))
        if external_id is None or title is None or job_url is None:
            raise SourcePayloadError(
                self.kind, "job detail is missing jobReqId, title, or externalUrl"
            )

        description_html = non_empty_string(info.get("jobDescription"))
        locations = self._locations(info, candidate.search_payload)
        is_remote = any("remote" in location.casefold() for location in locations)
        return DiscoveredJob(
            source=self.kind,
            source_identifier=f"{config.tenant}/{config.site}",
            external_id=external_id,
            company_name=config.company_name,
            title=title,
            locations=locations,
            description_text=html_to_text(description_html),
            description_html=description_html,
            employment_type=non_empty_string(info.get("timeType")),
            workplace_type=normalize_workplace(None, is_remote=is_remote),
            job_url=job_url,
            apply_url=job_url,
            published_at=parse_datetime(info.get("startDate")),
            compensation=self._compensation(description_html),
            raw_payload={"search": candidate.search_payload, "detail": dict(payload)},
        )

    @classmethod
    def _parse_search_page(cls, payload: Any) -> tuple[list[Mapping[str, Any]], int]:
        if not isinstance(payload, Mapping):
            raise SourcePayloadError(cls.kind, "search response is not an object")
        postings = payload.get("jobPostings")
        total = payload.get("total")
        if (
            not isinstance(postings, list)
            or isinstance(total, bool)
            or not isinstance(total, int)
            or total < 0
        ):
            raise SourcePayloadError(cls.kind, "search response has invalid postings or total")
        if any(not isinstance(item, Mapping) for item in postings):
            raise SourcePayloadError(cls.kind, "search postings contain a non-object item")
        return postings, total

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
    def _locations(info: Mapping[str, Any], search_payload: Mapping[str, Any]) -> tuple[str, ...]:
        values: list[object] = [info.get("location"), search_payload.get("locationsText")]
        additional = info.get("additionalLocations")
        if isinstance(additional, list):
            values.extend(
                item.get("descriptor") if isinstance(item, Mapping) else item for item in additional
            )
        return unique_strings(
            value
            for value in values
            if not (
                isinstance(value, str)
                and re.fullmatch(r"\d+ Locations?", value.strip(), re.IGNORECASE)
            )
        )

    @staticmethod
    def _base_url(config: WorkdaySourceConfig) -> str:
        if config.api_base_url:
            return config.api_base_url.rstrip("/")
        tenant = quote(config.tenant.strip(), safe="")
        site = quote(config.site.strip(), safe="")
        return f"https://{tenant}.wd5.myworkdayjobs.com/wday/cxs/{tenant}/{site}"

    @staticmethod
    def _compensation(description_html: str | None) -> Compensation | None:
        description = html_to_text(description_html)
        ranges = [*_USD_RANGE.findall(description), *_DOLLAR_RANGE.findall(description)]
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
