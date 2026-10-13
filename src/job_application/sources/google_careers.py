"""Google Careers public search adapter."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar
from urllib.parse import quote_plus

import httpx

from job_application.domain.models import (
    Compensation,
    DiscoveredJob,
    GoogleCareersSourceConfig,
    SourceKind,
)
from job_application.sources.base import JobSource
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.utils import (
    html_to_text,
    non_empty_string,
    parse_datetime,
    unique_strings,
)

_SCRIPT_MARKER = '<script class="ds:1"'
_DATA_MARKER = "data:"
_SIDE_CHANNEL_MARKER = ", sideChannel:"
_US_COMPENSATION = re.compile(r"US:\s*\$([\d,]+)\s*-\s*\$([\d,]+)\s*\(([A-Z]{3})\)", re.IGNORECASE)


@dataclass(frozen=True)
class _SearchPage:
    jobs: list[list[Any]]
    total: int
    page_size: int


class GoogleCareersSource(JobSource[GoogleCareersSourceConfig]):
    """Fetch one or more public Google Careers organization searches."""

    kind: ClassVar[SourceKind] = SourceKind.GOOGLE_CAREERS

    async def list_jobs(self, config: GoogleCareersSourceConfig) -> list[DiscoveredJob]:
        url = config.api_base_url.rstrip("/")
        search_texts = config.search_texts or ("",)
        seen_ids: set[str] = set()
        jobs: list[DiscoveredJob] = []

        async with self.client_session() as client:
            for search_text in search_texts:
                for job in await self._list_search(client, config, url, search_text):
                    if job.external_id in seen_ids:
                        continue
                    seen_ids.add(job.external_id)
                    jobs.append(job)
        return jobs

    async def _list_search(
        self,
        client: httpx.AsyncClient,
        config: GoogleCareersSourceConfig,
        url: str,
        search_text: str,
    ) -> list[DiscoveredJob]:
        observed_totals: set[int] = set()
        seen_ids: set[str] = set()
        jobs: list[DiscoveredJob] = []

        for page_number in range(1, config.max_pages + 1):
            params: dict[str, str | int] = {
                "company": config.company_filter,
                "hl": config.locale,
                "page": page_number,
            }
            if search_text:
                params["q"] = search_text
            page_html = await self.get_text(
                client,
                url,
                params=params,
                headers={"Accept": "text/html,application/xhtml+xml"},
            )
            try:
                page = self._parse_page(page_html)
            except SourcePayloadError as exc:
                raise SourcePayloadError(
                    self.kind, f"query {search_text!r} returned invalid search data: {exc}"
                ) from exc

            candidate_totals = observed_totals | {page.total}
            if observed_totals and (
                max(candidate_totals) - min(candidate_totals) > config.max_total_drift
            ):
                expected_total = min(observed_totals)
                raise SourcePayloadError(
                    self.kind,
                    f"job total changed during pagination for query {search_text!r}: "
                    f"{expected_total} to {page.total}",
                )
            observed_totals.add(page.total)

            for raw in page.jobs:
                external_id = non_empty_string(self._field(raw, 0))
                if external_id is None:
                    raise SourcePayloadError(self.kind, "job is missing an external ID")
                if external_id in seen_ids:
                    if config.allow_partial_results or config.max_total_drift:
                        continue
                    raise SourcePayloadError(
                        self.kind,
                        f"duplicate job {external_id} across pages for query {search_text!r}",
                    )
                seen_ids.add(external_id)
                jobs.append(self._normalize_job(config, raw))

            if len(jobs) >= max(observed_totals):
                break
            if not page.jobs:
                break
            if page.page_size <= 0:
                raise SourcePayloadError(self.kind, "search page reports an invalid page size")
        else:
            if not config.allow_partial_results:
                raise SourcePayloadError(
                    self.kind,
                    f"query {search_text!r} exceeded configured max_pages={config.max_pages}",
                )

        if not observed_totals:
            raise SourcePayloadError(self.kind, "search did not return a total job count")
        required_total = min(observed_totals)
        if len(jobs) < required_total and not config.allow_partial_results:
            total_summary = (
                str(required_total)
                if len(observed_totals) == 1
                else f"{required_total}-{max(observed_totals)}"
            )
            raise SourcePayloadError(
                self.kind,
                f"incomplete pagination for query {search_text!r}: "
                f"expected at least {total_summary} jobs, received {len(jobs)}",
            )
        return jobs

    def _normalize_job(self, config: GoogleCareersSourceConfig, raw: list[Any]) -> DiscoveredJob:
        external_id = non_empty_string(self._field(raw, 0))
        title = non_empty_string(self._field(raw, 1))
        organization = non_empty_string(self._field(raw, 7))
        if external_id is None or title is None:
            raise SourcePayloadError(self.kind, "job is missing an external ID or title")
        if organization is None or organization.casefold() != config.company_filter.casefold():
            raise SourcePayloadError(
                self.kind,
                "search returned organization "
                f"{organization!r}, expected {config.company_filter!r}",
            )

        responsibilities_html = self._wrapped_html(self._field(raw, 3))
        qualifications_html = self._wrapped_html(self._field(raw, 4))
        about_html = self._wrapped_html(self._field(raw, 10))
        description_html = "\n".join(
            part for part in (about_html, responsibilities_html, qualifications_html) if part
        )

        return DiscoveredJob(
            source=self.kind,
            source_identifier=config.company_filter,
            external_id=external_id,
            company_name=config.company_name,
            title=title,
            locations=self._locations(self._field(raw, 9)),
            description_text=html_to_text(description_html),
            description_html=description_html or None,
            employment_type=("Fixed-Term Contract" if "fixed-term" in title.casefold() else None),
            departments=(organization,),
            job_url=self._job_url(config, external_id, title),
            apply_url=non_empty_string(self._field(raw, 2)),
            published_at=self._proto_datetime(self._field(raw, 12)),
            source_updated_at=self._proto_datetime(self._field(raw, 13)),
            compensation=self._compensation(about_html),
            raw_payload={"job": raw},
        )

    @classmethod
    def _parse_page(cls, page_html: str) -> _SearchPage:
        script_start = page_html.find(_SCRIPT_MARKER)
        data_start = page_html.find(_DATA_MARKER, script_start)
        data_end = page_html.find(_SIDE_CHANNEL_MARKER, data_start)
        if script_start < 0 or data_start < 0 or data_end < 0:
            raise SourcePayloadError(cls.kind, "could not locate Google Careers search data")

        try:
            payload = json.loads(page_html[data_start + len(_DATA_MARKER) : data_end])
        except json.JSONDecodeError as exc:
            raise SourcePayloadError(
                cls.kind, "Google Careers search data is invalid JSON"
            ) from exc

        if not isinstance(payload, list) or len(payload) < 4:
            raise SourcePayloadError(cls.kind, "Google Careers search data has an invalid shape")
        raw_jobs, total, raw_page_size = payload[0], payload[2], payload[3]
        empty_result = raw_jobs in (None, []) and total == 0
        normalized_jobs = [] if raw_jobs is None else raw_jobs
        if (
            not isinstance(normalized_jobs, list)
            or isinstance(total, bool)
            or not isinstance(total, int)
            or (
                not empty_result
                and (isinstance(raw_page_size, bool) or not isinstance(raw_page_size, int))
            )
        ):
            raise SourcePayloadError(
                cls.kind,
                "Google Careers pagination metadata is invalid "
                f"(jobs={type(raw_jobs).__name__}, total={total!r}, "
                f"page_size={raw_page_size!r})",
            )
        if any(not isinstance(raw, list) for raw in normalized_jobs):
            raise SourcePayloadError(cls.kind, "Google Careers jobs list contains an invalid item")
        page_size = 0 if empty_result else raw_page_size
        assert isinstance(page_size, int)
        return _SearchPage(jobs=normalized_jobs, total=total, page_size=page_size)

    @staticmethod
    def _field(raw: list[Any], index: int) -> Any:
        return raw[index] if index < len(raw) else None

    @staticmethod
    def _wrapped_html(value: object) -> str:
        if isinstance(value, list) and len(value) > 1 and isinstance(value[1], str):
            return value[1]
        return ""

    @staticmethod
    def _locations(value: object) -> tuple[str, ...]:
        if not isinstance(value, list):
            return ()
        return unique_strings(item[0] for item in value if isinstance(item, list) and item)

    @staticmethod
    def _proto_datetime(value: object) -> datetime | None:
        if not isinstance(value, list) or not value:
            return None
        return parse_datetime(value[0])

    @staticmethod
    def _job_url(config: GoogleCareersSourceConfig, external_id: str, title: str) -> str:
        ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.casefold()).strip("-")
        company = quote_plus(config.company_filter)
        return f"{config.api_base_url.rstrip('/')}/{external_id}-{slug}?company={company}"

    @staticmethod
    def _compensation(about_html: str) -> Compensation | None:
        match = _US_COMPENSATION.search(html_to_text(about_html))
        if match is None:
            return None
        minimum = float(match.group(1).replace(",", ""))
        maximum = float(match.group(2).replace(",", ""))
        currency = match.group(3).upper()
        return Compensation(
            summary=f"${minimum:,.0f} - ${maximum:,.0f} ({currency})",
            currency=currency,
            interval="year",
            min_value=minimum,
            max_value=maximum,
            raw={"text": match.group(0)},
        )
