"""Adapter for the official Microsoft AI careers website."""

from __future__ import annotations

import asyncio
import re
from html.parser import HTMLParser
from typing import ClassVar
from urllib.parse import urljoin, urlparse

import httpx

from job_application.domain.models import (
    Compensation,
    DiscoveredJob,
    MicrosoftAiCareersSourceConfig,
    SourceKind,
)
from job_application.sources.base import JobSource
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.utils import html_to_text, unique_strings

_USD_RANGE = re.compile(
    r"USD\s*\$([\d,]+(?:\.\d+)?)\s*[\u2013\u2014-]\s*"
    r"\$([\d,]+(?:\.\d+)?)\s+per year",
    re.IGNORECASE,
)
_JOB_PATH = re.compile(r"^/careers/job/(?P<greenhouse_id>\d+)/[^/]+/?$")
_BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
    ),
}


class _CareersLinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "a":
            return
        href = dict(attrs).get("href")
        if not href:
            return
        absolute = urljoin(self.base_url, href)
        match = _JOB_PATH.match(urlparse(absolute).path)
        if match:
            self.links.setdefault(match.group("greenhouse_id"), absolute)


class _JobPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.metadata: dict[str, str] = {}
        self.description_html_parts: list[str] = []
        self._capture_title = False
        self._capture_meta: str | None = None
        self._meta_parts: list[str] = []
        self._description_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag.casefold() == "h1" and not self.title_parts:
            self._capture_title = True
        if tag.casefold() in {"dt", "dd"}:
            self._capture_meta = tag.casefold()
            self._meta_parts = []

        classes = (attributes.get("class") or "").split()
        if tag.casefold() == "div" and "greenhouse-wysiwyg" in classes:
            self._description_depth = 1
            return
        if self._description_depth:
            if tag.casefold() == "div":
                self._description_depth += 1
            self.description_html_parts.append(self.get_starttag_text() or f"<{tag}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if self._description_depth:
            self.description_html_parts.append(self.get_starttag_text() or f"<{tag}/>")

    def handle_endtag(self, tag: str) -> None:
        if self._capture_title and tag.casefold() == "h1":
            self._capture_title = False
        if self._capture_meta == "dt" and tag.casefold() == "dt":
            self._capture_meta = "label"
        elif self._capture_meta == "dd" and tag.casefold() == "dd":
            value = html_to_text("".join(self._meta_parts))
            label = self.metadata.pop("__pending_label", "")
            if label:
                self.metadata[label] = value
            self._capture_meta = None
            self._meta_parts = []
        elif self._capture_meta == "label" and tag.casefold() == "div":
            self._capture_meta = None

        if self._description_depth:
            if tag.casefold() == "div":
                self._description_depth -= 1
                if not self._description_depth:
                    return
            self.description_html_parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self.title_parts.append(data)
        if self._capture_meta in {"dt", "dd"}:
            self._meta_parts.append(data)
        if self._capture_meta == "dt":
            self.metadata["__pending_label"] = html_to_text("".join(self._meta_parts))
        if self._description_depth:
            self.description_html_parts.append(data)

    @property
    def title(self) -> str:
        return html_to_text("".join(self.title_parts))

    @property
    def description_html(self) -> str:
        return "".join(self.description_html_parts).strip()


class MicrosoftAiCareersSource(JobSource[MicrosoftAiCareersSourceConfig]):
    """Discover and normalize current jobs published on microsoft.ai."""

    kind: ClassVar[SourceKind] = SourceKind.MICROSOFT_AI_CAREERS

    async def list_jobs(self, config: MicrosoftAiCareersSourceConfig) -> list[DiscoveredJob]:
        base_url = config.api_base_url.rstrip("/") + "/"
        careers_url = urljoin(base_url, config.careers_path.lstrip("/"))
        async with self.client_session() as client:
            listing_html = await self.get_text(client, careers_url, headers=_BROWSER_HEADERS)
            links = self._parse_listing(listing_html, careers_url)
            if not links:
                raise SourcePayloadError(self.kind, "official careers page contains no job links")
            if len(links) > config.max_details:
                raise SourcePayloadError(
                    self.kind,
                    f"careers page has {len(links)} jobs, exceeding "
                    f"max_details={config.max_details}",
                )
            jobs = await self._fetch_details(client, config, links)
        return sorted(jobs, key=lambda job: (job.title.casefold(), job.external_id))

    @staticmethod
    def _parse_listing(html: str, careers_url: str) -> list[tuple[str, str]]:
        parser = _CareersLinkParser(careers_url)
        parser.feed(html)
        parser.close()
        return list(parser.links.items())

    async def _fetch_details(
        self,
        client: httpx.AsyncClient,
        config: MicrosoftAiCareersSourceConfig,
        links: list[tuple[str, str]],
    ) -> list[DiscoveredJob]:
        semaphore = asyncio.Semaphore(config.detail_concurrency)
        required = tuple(
            self._normalized(text) for text in config.required_any_texts if text.strip()
        )
        excluded = tuple(
            self._normalized(text) for text in config.excluded_any_texts if text.strip()
        )

        async def fetch(greenhouse_id: str, url: str) -> DiscoveredJob | None:
            async with semaphore:
                html = await self.get_text(client, url, headers=_BROWSER_HEADERS)
            job = self._parse_job(config, greenhouse_id, url, html)
            searchable = self._normalized(f"{job.title}\n{job.description_text}")
            if required and not any(text in searchable for text in required):
                return None
            if any(text in searchable for text in excluded):
                return None
            return job

        results = await asyncio.gather(*(fetch(identifier, url) for identifier, url in links))
        return [job for job in results if job is not None]

    def _parse_job(
        self,
        config: MicrosoftAiCareersSourceConfig,
        greenhouse_id: str,
        url: str,
        html: str,
    ) -> DiscoveredJob:
        parser = _JobPageParser()
        parser.feed(html)
        parser.close()
        external_id = parser.metadata.get("Job Number", "").strip()
        location = parser.metadata.get("Location", "").strip()
        if not location:
            city = parser.metadata.get("City", "").strip()
            state = parser.metadata.get("State", "").strip()
            country = parser.metadata.get("Country", "").strip()
            # Some roles list only a region (e.g. City: North America).
            # Preserve exactly the supplied geography without inventing a country.
            location = ", ".join(unique_strings([city, state, country]))
        missing = [
            name
            for name, value in (
                ("title", parser.title),
                ("Job Number", external_id),
                ("Location or City/State/Country", location),
                ("description", parser.description_html),
            )
            if not value
        ]
        if missing:
            raise SourcePayloadError(
                self.kind,
                f"job {greenhouse_id} is missing {', '.join(missing)}",
            )
        locations = unique_strings(part.strip() for part in re.split(r"\s*(?:·|\||;)\s*", location))
        team = parser.metadata.get("Team", "").strip()
        discipline = parser.metadata.get("Discipline", "").strip()
        return DiscoveredJob(
            source=self.kind,
            source_identifier=urlparse(config.api_base_url).netloc or "microsoft.ai",
            external_id=external_id,
            company_name=config.company_name,
            title=parser.title,
            locations=locations,
            description_text=html_to_text(parser.description_html),
            description_html=parser.description_html,
            departments=(discipline,) if discipline else (),
            teams=(team,) if team else (),
            job_url=url,
            apply_url=f"{url.rstrip('/')}#apply",
            compensation=self._compensation(parser.description_html),
            raw_payload={
                "greenhouse_id": greenhouse_id,
                "metadata": parser.metadata,
            },
        )

    @staticmethod
    def _normalized(value: str) -> str:
        return re.sub(r"\s+", " ", value.replace("\u2019", "'")).strip().casefold()

    @staticmethod
    def _compensation(description_html: str) -> Compensation | None:
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
