"""Amazon public jobs search adapter."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, ClassVar
from urllib.parse import urljoin

from job_application.domain.models import (
    AmazonJobsSourceConfig,
    DiscoveredJob,
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


class AmazonJobsSource(JobSource[AmazonJobsSourceConfig]):
    """Fetch and normalize a deduplicated union of Amazon job searches."""

    kind: ClassVar[SourceKind] = SourceKind.AMAZON_JOBS

    async def list_jobs(self, config: AmazonJobsSourceConfig) -> list[DiscoveredJob]:
        search_texts = tuple(value.strip() for value in config.search_texts if value.strip()) or (
            "",
        )
        raw_jobs: dict[str, Mapping[str, Any]] = {}
        url = f"{config.api_base_url.rstrip('/')}/en/search.json"

        async with self.client_session() as client:
            for search_text in search_texts:
                fetched = 0
                for page in range(config.max_pages_per_search):
                    payload = await self.get_json(
                        client,
                        url,
                        params={
                            "base_query": search_text,
                            "offset": page * config.page_size,
                            "result_limit": config.page_size,
                        },
                    )
                    jobs, total = self._parse_search_page(payload)
                    for raw in jobs:
                        identifier = non_empty_string(raw.get("id_icims") or raw.get("id"))
                        if identifier is None:
                            raise SourcePayloadError(self.kind, "Amazon result is missing id")
                        raw_jobs.setdefault(identifier, raw)
                    fetched += len(jobs)
                    if fetched >= total:
                        break
                    if not jobs:
                        raise SourcePayloadError(
                            self.kind,
                            f"empty Amazon search page for {search_text!r} before total={total}",
                        )
                else:
                    raise SourcePayloadError(
                        self.kind,
                        f"Amazon search {search_text!r} exceeded max_pages_per_search="
                        f"{config.max_pages_per_search}",
                    )

        return sorted(
            (self._normalize_job(config, identifier, raw) for identifier, raw in raw_jobs.items()),
            key=lambda job: (job.title.casefold(), job.external_id),
        )

    @classmethod
    def _parse_search_page(cls, payload: Any) -> tuple[list[Mapping[str, Any]], int]:
        if not isinstance(payload, Mapping):
            raise SourcePayloadError(cls.kind, "Amazon search response is not an object")
        jobs = payload.get("jobs")
        total = payload.get("hits")
        if (
            not isinstance(jobs, list)
            or any(not isinstance(item, Mapping) for item in jobs)
            or isinstance(total, bool)
            or not isinstance(total, int)
            or total < 0
        ):
            raise SourcePayloadError(cls.kind, "Amazon search jobs or hits are invalid")
        return jobs, total

    def _normalize_job(
        self,
        config: AmazonJobsSourceConfig,
        identifier: str,
        raw: Mapping[str, Any],
    ) -> DiscoveredJob:
        title = non_empty_string(raw.get("title"))
        path = non_empty_string(raw.get("job_path"))
        if title is None or path is None:
            raise SourcePayloadError(self.kind, "Amazon result is missing title or job_path")

        locations: list[object] = []
        raw_locations = raw.get("locations")
        if isinstance(raw_locations, list):
            for value in raw_locations:
                if isinstance(value, str):
                    try:
                        location = json.loads(value)
                    except json.JSONDecodeError:
                        locations.append(value)
                        continue
                else:
                    location = value
                if isinstance(location, Mapping):
                    locations.append(
                        location.get("normalizedLocation")
                        or location.get("locationNonStemming")
                        or location.get("location")
                    )
        locations.extend([raw.get("normalized_location"), raw.get("location")])
        normalized_locations = unique_strings(locations)
        description = "\n".join(
            unique_strings(
                [
                    html_to_text(raw.get("description")),
                    html_to_text(raw.get("basic_qualifications")),
                    html_to_text(raw.get("preferred_qualifications")),
                ]
            )
        )
        job_url = urljoin(f"{config.api_base_url.rstrip('/')}/", path)
        return DiscoveredJob(
            source=self.kind,
            source_identifier="amazon.jobs",
            external_id=identifier,
            company_name=config.company_name,
            title=title,
            locations=normalized_locations,
            description_text=description,
            employment_type=non_empty_string(raw.get("job_schedule_type")),
            workplace_type=normalize_workplace(
                "remote"
                if any("remote" in value.casefold() for value in normalized_locations)
                else None
            ),
            departments=unique_strings([raw.get("job_category"), raw.get("job_family")]),
            teams=unique_strings([raw.get("team")]),
            job_url=job_url,
            apply_url=non_empty_string(raw.get("url_next_step")) or job_url,
            published_at=parse_datetime(raw.get("posted_date")),
            source_updated_at=parse_datetime(raw.get("updated_time")),
            raw_payload=dict(raw),
        )
