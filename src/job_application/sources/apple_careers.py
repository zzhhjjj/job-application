"""Apple public careers search adapter."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any, ClassVar
from urllib.parse import quote

from job_application.domain.models import (
    AppleCareersSourceConfig,
    DiscoveredJob,
    SourceKind,
)
from job_application.sources.base import JobSource
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.utils import (
    non_empty_string,
    normalize_workplace,
    parse_datetime,
    unique_strings,
)

_HYDRATION = re.compile(
    r"window\.__staticRouterHydrationData\s*=\s*JSON\.parse\((?P<payload>\"(?:\\.|[^\"\\])*\")\);",
    re.DOTALL,
)


class AppleCareersSource(JobSource[AppleCareersSourceConfig]):
    """Read Apple's SSR hydration payload and combine multi-location postings."""

    kind: ClassVar[SourceKind] = SourceKind.APPLE_CAREERS

    async def list_jobs(self, config: AppleCareersSourceConfig) -> list[DiscoveredJob]:
        url = f"{config.api_base_url.rstrip('/')}/{quote(config.locale, safe='')}/search"
        grouped: dict[str, list[Mapping[str, Any]]] = {}
        fetched = 0

        async with self.client_session() as client:
            for page in range(1, config.max_pages + 1):
                html = await self.get_text(
                    client,
                    url,
                    params={
                        "location": config.location_filter,
                        "team": config.team_filter,
                        "page": page,
                    },
                    headers={"Accept": "text/html,application/xhtml+xml"},
                )
                results, total = self._parse_search_page(html)
                for raw in results:
                    identifier = non_empty_string(raw.get("positionId") or raw.get("reqId"))
                    if identifier is None:
                        raise SourcePayloadError(self.kind, "search result is missing positionId")
                    grouped.setdefault(identifier, []).append(raw)
                fetched += len(results)
                if fetched >= total:
                    break
                if not results:
                    raise SourcePayloadError(
                        self.kind, f"empty Apple search page {page} before total={total}"
                    )
            else:
                raise SourcePayloadError(
                    self.kind,
                    f"Apple search exceeded max_pages={config.max_pages}",
                )

        return sorted(
            (self._normalize_job(config, identifier, rows) for identifier, rows in grouped.items()),
            key=lambda job: (job.title.casefold(), job.external_id),
        )

    @classmethod
    def _parse_search_page(cls, html: str) -> tuple[list[Mapping[str, Any]], int]:
        match = _HYDRATION.search(html)
        if match is None:
            raise SourcePayloadError(cls.kind, "Apple page is missing hydration data")
        try:
            payload_text = json.loads(match.group("payload"))
            payload = json.loads(payload_text)
            search = payload["loaderData"]["search"]
            results = search["searchResults"]
            total = search["totalRecords"]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise SourcePayloadError(cls.kind, "Apple hydration data has an invalid shape") from exc
        if (
            not isinstance(results, list)
            or any(not isinstance(item, Mapping) for item in results)
            or isinstance(total, bool)
            or not isinstance(total, int)
            or total < 0
        ):
            raise SourcePayloadError(cls.kind, "Apple search results or total are invalid")
        return results, total

    def _normalize_job(
        self,
        config: AppleCareersSourceConfig,
        identifier: str,
        rows: list[Mapping[str, Any]],
    ) -> DiscoveredJob:
        first = rows[0]
        title = non_empty_string(first.get("postingTitle"))
        request_id = non_empty_string(first.get("reqId"))
        slug = non_empty_string(first.get("transformedPostingTitle"))
        if title is None or request_id is None or slug is None:
            raise SourcePayloadError(self.kind, "Apple result is missing title, reqId, or slug")

        locations: list[str] = []
        for row in rows:
            raw_locations = row.get("locations")
            if not isinstance(raw_locations, list):
                continue
            for raw_location in raw_locations:
                if not isinstance(raw_location, Mapping):
                    continue
                location = ", ".join(
                    unique_strings(
                        [
                            raw_location.get("name") or raw_location.get("city"),
                            raw_location.get("stateProvince"),
                            raw_location.get("countryName"),
                        ]
                    )
                )
                if location:
                    locations.append(location)

        descriptions = unique_strings(row.get("jobSummary") for row in rows)
        team = first.get("team")
        team_name = team.get("teamName") if isinstance(team, Mapping) else None
        job_url = (
            f"{config.api_base_url.rstrip('/')}/{quote(config.locale, safe='')}/details/"
            f"{quote(request_id, safe='-')}/{quote(slug, safe='-')}"
        )
        normalized_locations = unique_strings(locations)
        return DiscoveredJob(
            source=self.kind,
            source_identifier="jobs.apple.com",
            external_id=identifier,
            company_name=config.company_name,
            title=title,
            locations=normalized_locations,
            description_text="\n".join(descriptions),
            workplace_type=normalize_workplace(
                "remote"
                if any("remote" in value.casefold() for value in normalized_locations)
                else None
            ),
            teams=unique_strings([team_name]),
            job_url=job_url,
            apply_url=job_url,
            published_at=parse_datetime(first.get("postDateInGMT")),
            raw_payload={"searchResults": [dict(row) for row in rows]},
        )
