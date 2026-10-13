"""Lever Postings API adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar
from urllib.parse import quote

from job_application.domain.models import (
    Compensation,
    DiscoveredJob,
    LeverRegion,
    LeverSourceConfig,
    SourceKind,
)
from job_application.sources.base import JobSource
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.utils import (
    ensure_mapping,
    float_or_none,
    html_to_text,
    non_empty_string,
    normalize_workplace,
    parse_datetime,
    unique_strings,
)

_LEVER_BASE_URLS = {
    LeverRegion.GLOBAL: "https://api.lever.co",
    LeverRegion.EU: "https://api.eu.lever.co",
}


class LeverSource(JobSource[LeverSourceConfig]):
    """Fetch and normalize all pages from a public Lever site."""

    kind: ClassVar[SourceKind] = SourceKind.LEVER

    async def list_jobs(self, config: LeverSourceConfig) -> list[DiscoveredJob]:
        base_url = config.api_base_url or _LEVER_BASE_URLS[config.region]
        site = quote(config.site.strip(), safe="")
        url = f"{base_url.rstrip('/')}/v0/postings/{site}"
        jobs: list[DiscoveredJob] = []
        seen_external_ids: set[str] = set()
        skip = 0

        async with self.client_session() as client:
            for _page_number in range(config.max_pages):
                payload = await self.get_json(
                    client,
                    url,
                    params={"mode": "json", "skip": skip, "limit": config.page_size},
                )
                if not isinstance(payload, list):
                    raise SourcePayloadError(self.kind, "expected a JSON list of postings")
                if not payload:
                    return jobs

                new_in_page = 0
                for item in payload:
                    if not isinstance(item, Mapping):
                        raise SourcePayloadError(
                            self.kind, "postings list contains a non-object item"
                        )
                    normalized = self._normalize_job(config, item)
                    if normalized.external_id in seen_external_ids:
                        continue
                    seen_external_ids.add(normalized.external_id)
                    jobs.append(normalized)
                    new_in_page += 1

                if len(payload) < config.page_size:
                    return jobs
                if new_in_page == 0:
                    raise SourcePayloadError(
                        self.kind, "pagination repeated a page without any new posting IDs"
                    )
                skip += len(payload)

        raise SourcePayloadError(
            self.kind, f"pagination exceeded configured max_pages={config.max_pages}"
        )

    def _normalize_job(self, config: LeverSourceConfig, raw: Mapping[str, Any]) -> DiscoveredJob:
        external_id = non_empty_string(raw.get("id"))
        title = non_empty_string(raw.get("text"))
        job_url = non_empty_string(raw.get("hostedUrl"))
        if not external_id or not title or not job_url:
            raise SourcePayloadError(
                self.kind, "posting is missing one of the required fields: id, text, hostedUrl"
            )

        categories = ensure_mapping(raw.get("categories")) or {}
        raw_locations = categories.get("allLocations")
        if not isinstance(raw_locations, list):
            raw_locations = [categories.get("location")]

        description_html = non_empty_string(raw.get("description"))
        if description_html is None:
            description_html = self._compose_description_html(raw)
        description_text = non_empty_string(raw.get("descriptionPlain"))
        if description_text is None:
            description_text = html_to_text(description_html)

        departments = unique_strings([categories.get("department")])
        teams = unique_strings([categories.get("team")])

        return DiscoveredJob(
            source=self.kind,
            source_identifier=config.site,
            external_id=external_id,
            company_name=config.company_name,
            title=title,
            locations=unique_strings(raw_locations),
            description_text=description_text,
            description_html=description_html,
            employment_type=non_empty_string(categories.get("commitment")),
            workplace_type=normalize_workplace(raw.get("workplaceType")),
            departments=departments,
            teams=teams,
            job_url=job_url,
            apply_url=non_empty_string(raw.get("applyUrl")),
            published_at=parse_datetime(raw.get("createdAt")),
            source_updated_at=parse_datetime(raw.get("updatedAt")),
            compensation=self._compensation(raw),
            raw_payload=dict(raw),
        )

    @staticmethod
    def _compose_description_html(raw: Mapping[str, Any]) -> str | None:
        parts: list[str] = []
        for key in ("opening", "descriptionBody"):
            value = non_empty_string(raw.get(key))
            if value:
                parts.append(value)
        lists = raw.get("lists")
        if isinstance(lists, list):
            for item in lists:
                if not isinstance(item, Mapping):
                    continue
                heading = non_empty_string(item.get("text"))
                content = non_empty_string(item.get("content"))
                if heading:
                    parts.append(f"<h3>{heading}</h3>")
                if content:
                    parts.append(f"<ul>{content}</ul>")
        additional = non_empty_string(raw.get("additional"))
        if additional:
            parts.append(additional)
        return "\n".join(parts) or None

    @staticmethod
    def _compensation(raw: Mapping[str, Any]) -> Compensation | None:
        salary_range = ensure_mapping(raw.get("salaryRange"))
        if salary_range is None:
            return None
        return Compensation(
            summary=non_empty_string(raw.get("salaryDescriptionPlain")),
            currency=non_empty_string(salary_range.get("currency")),
            interval=non_empty_string(salary_range.get("interval")),
            min_value=float_or_none(salary_range.get("min")),
            max_value=float_or_none(salary_range.get("max")),
            raw=dict(salary_range),
        )
