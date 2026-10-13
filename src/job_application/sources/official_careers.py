"""Adapter for verified roles on official careers sites without a board API."""

from __future__ import annotations

import asyncio
from typing import ClassVar
from xml.etree import ElementTree

import httpx

from job_application.domain.models import (
    DiscoveredJob,
    OfficialCareersSourceConfig,
    OfficialPosting,
    SourceKind,
)
from job_application.sources.base import JobSource
from job_application.sources.exceptions import SourceRequestError
from job_application.sources.utils import html_to_text


class OfficialCareersSource(JobSource[OfficialCareersSourceConfig]):
    """Keep configured official postings only while their public pages remain active."""

    kind: ClassVar[SourceKind] = SourceKind.OFFICIAL_CAREERS

    # Only an explicit HTTP 404/410 confirms closure; a missing page marker is unknown.
    closed_ids: set[str]
    unverified_ids: set[str]

    async def list_jobs(self, config: OfficialCareersSourceConfig) -> list[DiscoveredJob]:
        self.closed_ids = set()
        self.unverified_ids = set()
        async with self.client_session() as client:
            results = await asyncio.gather(
                *(self._fetch_posting(client, config, posting) for posting in config.postings)
            )
        return [job for job in results if job is not None]

    async def _fetch_posting(
        self,
        client: httpx.AsyncClient,
        config: OfficialCareersSourceConfig,
        posting: OfficialPosting,
    ) -> DiscoveredJob | None:
        try:
            response = await client.get(
                posting.job_url,
                headers={"Accept": "text/html,application/xhtml+xml"},
            )
            if response.status_code in {404, 410}:
                self.closed_ids.add(posting.external_id)
                return None
            if response.status_code == 403:
                listed = await self._is_listed_in_active_index(client, posting)
                if listed is True:
                    return self._job_from_posting(config, posting)
                if listed is False:
                    return None
                if posting.retain_on_forbidden:
                    self.unverified_ids.add(posting.external_id)
                    return self._job_from_posting(config, posting)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SourceRequestError(
                self.kind, f"request failed for {posting.job_url}: {exc}"
            ) from exc

        page_text = html_to_text(response.text)
        marker = posting.active_marker or posting.title
        if marker.casefold() not in page_text.casefold():
            return None

        return self._job_from_posting(config, posting)

    async def _is_listed_in_active_index(
        self, client: httpx.AsyncClient, posting: OfficialPosting
    ) -> bool | None:
        """Check an official sitemap/listing when a detail page is bot-blocked."""
        if posting.active_index_url is None:
            return None
        try:
            response = await client.get(
                posting.active_index_url,
                headers={"Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8"},
            )
            response.raise_for_status()
            root = ElementTree.fromstring(response.text)
        except (httpx.HTTPError, ElementTree.ParseError):
            return None

        target = posting.job_url.rstrip("/")
        return any(
            element.text is not None and element.text.strip().rstrip("/") == target
            for element in root.findall(".//{*}loc")
        )

    def _job_from_posting(
        self, config: OfficialCareersSourceConfig, posting: OfficialPosting
    ) -> DiscoveredJob:
        return DiscoveredJob(
            source=self.kind,
            source_identifier=config.company_name,
            external_id=posting.external_id,
            company_name=config.company_name,
            title=posting.title,
            locations=posting.locations,
            description_text=posting.description_text,
            job_url=posting.job_url,
            apply_url=posting.job_url,
        )
