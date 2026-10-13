"""Greenhouse Job Board API adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar
from urllib.parse import quote

from job_application.domain.models import (
    DiscoveredJob,
    GreenhouseSourceConfig,
    SourceKind,
)
from job_application.sources.base import JobSource
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.utils import (
    html_to_text,
    names_from_mappings,
    non_empty_string,
    parse_datetime,
    unique_strings,
)


class GreenhouseSource(JobSource[GreenhouseSourceConfig]):
    """Fetch and normalize a complete public Greenhouse board."""

    kind: ClassVar[SourceKind] = SourceKind.GREENHOUSE

    async def list_jobs(self, config: GreenhouseSourceConfig) -> list[DiscoveredJob]:
        token = quote(config.board_token.strip(), safe="")
        url = f"{config.api_base_url.rstrip('/')}/v1/boards/{token}/jobs"
        async with self.client_session() as client:
            payload = await self.get_json(client, url, params={"content": "true"})

        if not isinstance(payload, Mapping) or not isinstance(payload.get("jobs"), list):
            raise SourcePayloadError(self.kind, "expected an object containing a jobs list")

        jobs: list[DiscoveredJob] = []
        for item in payload["jobs"]:
            if not isinstance(item, Mapping):
                raise SourcePayloadError(self.kind, "jobs list contains a non-object item")
            jobs.append(self._normalize_job(config, item))
        return jobs

    def _normalize_job(
        self, config: GreenhouseSourceConfig, raw: Mapping[str, Any]
    ) -> DiscoveredJob:
        external_id = non_empty_string(raw.get("id"))
        title = non_empty_string(raw.get("title"))
        job_url = non_empty_string(raw.get("absolute_url"))
        if not external_id or not title or not job_url:
            raise SourcePayloadError(
                self.kind, "job is missing one of the required fields: id, title, absolute_url"
            )

        location = raw.get("location")
        primary_location = location.get("name") if isinstance(location, Mapping) else None
        office_locations = (
            item.get("location") for item in raw.get("offices", []) if isinstance(item, Mapping)
        )
        locations = unique_strings([primary_location, *office_locations])
        content = non_empty_string(raw.get("content"))

        return DiscoveredJob(
            source=self.kind,
            source_identifier=config.board_token,
            external_id=external_id,
            company_name=config.company_name,
            title=title,
            locations=locations,
            description_text=html_to_text(content),
            description_html=content,
            departments=names_from_mappings(raw.get("departments")),
            job_url=job_url,
            apply_url=job_url,
            published_at=parse_datetime(raw.get("first_published")),
            source_updated_at=parse_datetime(raw.get("updated_at")),
            raw_payload=dict(raw),
        )
