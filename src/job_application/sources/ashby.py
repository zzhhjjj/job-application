"""Ashby public Job Postings API adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar
from urllib.parse import quote

from job_application.domain.models import (
    AshbySourceConfig,
    Compensation,
    DiscoveredJob,
    SourceKind,
)
from job_application.sources.base import JobSource
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.utils import (
    ensure_mapping,
    external_id_from_url,
    float_or_none,
    html_to_text,
    non_empty_string,
    normalize_workplace,
    parse_datetime,
    unique_strings,
)


class AshbySource(JobSource[AshbySourceConfig]):
    """Fetch and normalize a complete public Ashby board."""

    kind: ClassVar[SourceKind] = SourceKind.ASHBY

    async def list_jobs(self, config: AshbySourceConfig) -> list[DiscoveredJob]:
        board = quote(config.job_board_name.strip(), safe="")
        url = f"{config.api_base_url.rstrip('/')}/posting-api/job-board/{board}"
        async with self.client_session() as client:
            payload = await self.get_json(
                client,
                url,
                params={"includeCompensation": str(config.include_compensation).lower()},
            )

        if not isinstance(payload, Mapping) or not isinstance(payload.get("jobs"), list):
            raise SourcePayloadError(self.kind, "expected an object containing a jobs list")

        jobs: list[DiscoveredJob] = []
        for item in payload["jobs"]:
            if not isinstance(item, Mapping):
                raise SourcePayloadError(self.kind, "jobs list contains a non-object item")
            if item.get("isListed") is False and not config.include_unlisted:
                continue
            jobs.append(self._normalize_job(config, item))
        return jobs

    def _normalize_job(self, config: AshbySourceConfig, raw: Mapping[str, Any]) -> DiscoveredJob:
        title = non_empty_string(raw.get("title"))
        job_url = non_empty_string(raw.get("jobUrl"))
        if not title or not job_url:
            raise SourcePayloadError(self.kind, "job is missing title or jobUrl")

        primary_location = non_empty_string(raw.get("location"))
        secondary_locations = raw.get("secondaryLocations")
        secondary_names: list[object] = []
        if isinstance(secondary_locations, list):
            secondary_names.extend(
                item.get("location") for item in secondary_locations if isinstance(item, Mapping)
            )

        external_id = non_empty_string(raw.get("id")) or external_id_from_url(
            job_url,
            fallback_parts=(config.job_board_name, title, primary_location or ""),
        )
        description_html = non_empty_string(raw.get("descriptionHtml"))
        description_text = non_empty_string(raw.get("descriptionPlain"))

        return DiscoveredJob(
            source=self.kind,
            source_identifier=config.job_board_name,
            external_id=external_id,
            company_name=config.company_name,
            title=title,
            locations=unique_strings([primary_location, *secondary_names]),
            description_text=description_text or html_to_text(description_html),
            description_html=description_html,
            employment_type=non_empty_string(raw.get("employmentType")),
            workplace_type=normalize_workplace(
                raw.get("workplaceType"),
                is_remote=raw.get("isRemote") if isinstance(raw.get("isRemote"), bool) else None,
            ),
            departments=unique_strings([raw.get("department")]),
            teams=unique_strings([raw.get("team")]),
            job_url=job_url,
            apply_url=non_empty_string(raw.get("applyUrl")),
            published_at=parse_datetime(raw.get("publishedAt")),
            compensation=self._compensation(raw),
            raw_payload=dict(raw),
        )

    @staticmethod
    def _compensation(raw: Mapping[str, Any]) -> Compensation | None:
        compensation = ensure_mapping(raw.get("compensation"))
        if compensation is None:
            return None

        salary_component: Mapping[str, Any] | None = None
        components = compensation.get("summaryComponents")
        if isinstance(components, list):
            salary_component = next(
                (
                    item
                    for item in components
                    if isinstance(item, Mapping)
                    and str(item.get("compensationType", "")).lower() == "salary"
                ),
                None,
            )

        return Compensation(
            summary=non_empty_string(
                compensation.get("scrapeableCompensationSalarySummary")
                or compensation.get("compensationTierSummary")
            ),
            currency=non_empty_string(salary_component.get("currencyCode"))
            if salary_component
            else None,
            interval=non_empty_string(salary_component.get("interval"))
            if salary_component
            else None,
            min_value=float_or_none(salary_component.get("minValue")) if salary_component else None,
            max_value=float_or_none(salary_component.get("maxValue")) if salary_component else None,
            raw=dict(compensation),
        )
