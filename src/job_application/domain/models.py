"""Validated domain models shared by job sources and persistence."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

JsonObject: TypeAlias = dict[str, Any]


class SourceKind(StrEnum):
    """Currently supported job-board providers."""

    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    GOOGLE_CAREERS = "google-careers"
    MICROSOFT_CAREERS = "microsoft-careers"
    MICROSOFT_AI_CAREERS = "microsoft-ai-careers"
    WORKDAY = "workday"
    APPLE_CAREERS = "apple-careers"
    AMAZON_JOBS = "amazon-jobs"
    OFFICIAL_CAREERS = "official-careers"


class LeverRegion(StrEnum):
    """Lever hosts separate global and EU API instances."""

    GLOBAL = "global"
    EU = "eu"


class WorkplaceType(StrEnum):
    """Normalized workplace arrangement."""

    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"
    UNSPECIFIED = "unspecified"


class JobStatus(StrEnum):
    """Lifecycle state of a tracked job."""

    ACTIVE = "active"
    CLOSED = "closed"


class Compensation(BaseModel):
    """Provider-neutral compensation summary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    summary: str | None = None
    currency: str | None = None
    interval: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    raw: JsonObject = Field(default_factory=dict)


class DiscoveredJob(BaseModel):
    """A normalized public job posting returned by any source adapter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source: SourceKind
    source_identifier: str = Field(min_length=1)
    external_id: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    locations: tuple[str, ...] = ()
    description_text: str = ""
    description_html: str | None = None
    employment_type: str | None = None
    workplace_type: WorkplaceType = WorkplaceType.UNSPECIFIED
    departments: tuple[str, ...] = ()
    teams: tuple[str, ...] = ()
    job_url: str = Field(min_length=1)
    apply_url: str | None = None
    published_at: datetime | None = None
    source_updated_at: datetime | None = None
    compensation: Compensation | None = None
    raw_payload: JsonObject = Field(default_factory=dict)

    @field_validator("locations", "departments", "teams", mode="before")
    @classmethod
    def normalize_string_sequence(cls, value: object) -> tuple[str, ...]:
        """Trim, remove empty values, and preserve first-seen order."""

        if value is None:
            return ()
        if isinstance(value, str):
            values: list[object] = [value]
        elif isinstance(value, Iterable):
            values = list(value)
        else:
            values = [value]

        result: list[str] = []
        seen: set[str] = set()
        for item in values:
            normalized = str(item).strip()
            if normalized and normalized not in seen:
                result.append(normalized)
                seen.add(normalized)
        return tuple(result)

    def normalized_payload(self) -> JsonObject:
        """Return stable provider-independent content suitable for snapshots."""

        return self.model_dump(mode="json", exclude={"raw_payload"})

    def content_hash(self) -> str:
        """Return a deterministic fingerprint for meaningful normalized content."""

        payload = self.normalized_payload()
        # Provider timestamps can change without a material edit. They are stored, but
        # do not create a new content snapshot on their own.
        payload.pop("source_updated_at", None)
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class BaseSourceConfig(BaseModel):
    """Fields common to all source configurations."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    company_name: str = Field(min_length=1)
    enabled: bool = True


class GreenhouseSourceConfig(BaseSourceConfig):
    """Configuration for a Greenhouse public job board."""

    source: Literal[SourceKind.GREENHOUSE] = SourceKind.GREENHOUSE
    board_token: str = Field(min_length=1)
    api_base_url: str = "https://boards-api.greenhouse.io"


class LeverSourceConfig(BaseSourceConfig):
    """Configuration for a Lever public postings site."""

    source: Literal[SourceKind.LEVER] = SourceKind.LEVER
    site: str = Field(min_length=1)
    region: LeverRegion = LeverRegion.GLOBAL
    api_base_url: str | None = None
    page_size: int = Field(default=100, ge=1, le=100)
    max_pages: int = Field(default=100, ge=1, le=1000)


class AshbySourceConfig(BaseSourceConfig):
    """Configuration for an Ashby public job board."""

    source: Literal[SourceKind.ASHBY] = SourceKind.ASHBY
    job_board_name: str = Field(min_length=1)
    api_base_url: str = "https://api.ashbyhq.com"
    include_compensation: bool = True
    include_unlisted: bool = False


class GoogleCareersSourceConfig(BaseSourceConfig):
    """Configuration for a filtered Google Careers public search."""

    source: Literal[SourceKind.GOOGLE_CAREERS] = SourceKind.GOOGLE_CAREERS
    company_filter: str = Field(min_length=1)
    search_texts: tuple[str, ...] = ()
    locale: str = Field(default="en-US", min_length=2)
    api_base_url: str = "https://www.google.com/about/careers/applications/jobs/results"
    max_pages: int = Field(default=20, ge=1, le=100)
    allow_partial_results: bool = False
    max_total_drift: int = Field(default=0, ge=0, le=10)


class MicrosoftCareersSourceConfig(BaseSourceConfig):
    """Configuration for the public Microsoft Eightfold careers site."""

    source: Literal[SourceKind.MICROSOFT_CAREERS] = SourceKind.MICROSOFT_CAREERS
    domain: str = Field(default="microsoft.com", min_length=1)
    api_base_url: str = "https://apply.careers.microsoft.com"
    search_texts: tuple[str, ...] = ()
    candidate_title_keywords: tuple[str, ...] = ()
    required_description_text: str | None = None
    excluded_description_texts: tuple[str, ...] = ()
    max_pages_per_search: int = Field(default=1, ge=1, le=100)
    page_size: int = Field(default=10, ge=1, le=100)
    max_details: int = Field(default=100, ge=1, le=1000)
    detail_concurrency: int = Field(default=3, ge=1, le=20)


class MicrosoftAiCareersSourceConfig(BaseSourceConfig):
    """Configuration for the official Microsoft AI careers website."""

    source: Literal[SourceKind.MICROSOFT_AI_CAREERS] = SourceKind.MICROSOFT_AI_CAREERS
    api_base_url: str = "https://microsoft.ai"
    careers_path: str = "/careers/"
    required_any_texts: tuple[str, ...] = ()
    excluded_any_texts: tuple[str, ...] = ()
    max_details: int = Field(default=100, ge=1, le=500)
    detail_concurrency: int = Field(default=8, ge=1, le=20)


class WorkdaySourceConfig(BaseSourceConfig):
    """Configuration for a public Workday candidate site."""

    source: Literal[SourceKind.WORKDAY] = SourceKind.WORKDAY
    tenant: str = Field(min_length=1)
    site: str = Field(min_length=1)
    api_base_url: str | None = None
    search_texts: tuple[str, ...] = ()
    candidate_title_keywords: tuple[str, ...] = ()
    page_size: int = Field(default=20, ge=1, le=20)
    max_pages_per_search: int = Field(default=100, ge=1, le=200)
    max_details: int = Field(default=500, ge=1, le=2000)
    detail_concurrency: int = Field(default=10, ge=1, le=30)


class AppleCareersSourceConfig(BaseSourceConfig):
    """Configuration for Apple's server-rendered public job search."""

    source: Literal[SourceKind.APPLE_CAREERS] = SourceKind.APPLE_CAREERS
    api_base_url: str = "https://jobs.apple.com"
    locale: str = Field(default="en-us", min_length=2)
    location_filter: str = "united-states-USA"
    team_filter: str = "machine-learning-infrastructure-MLAI-MLI"
    max_pages: int = Field(default=20, ge=1, le=100)


class AmazonJobsSourceConfig(BaseSourceConfig):
    """Configuration for Amazon's public job-search JSON endpoint."""

    source: Literal[SourceKind.AMAZON_JOBS] = SourceKind.AMAZON_JOBS
    api_base_url: str = "https://www.amazon.jobs"
    search_texts: tuple[str, ...] = ()
    page_size: int = Field(default=100, ge=1, le=100)
    max_pages_per_search: int = Field(default=10, ge=1, le=100)


class OfficialPosting(BaseModel):
    """One known role on a company's official careers website."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    external_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    locations: tuple[str, ...]
    job_url: str = Field(min_length=1)
    description_text: str = Field(min_length=1)
    active_marker: str | None = None
    active_index_url: str | None = None
    retain_on_forbidden: bool = False


class OfficialCareersSourceConfig(BaseSourceConfig):
    """Official job pages for companies without a supported public board API."""

    source: Literal[SourceKind.OFFICIAL_CAREERS] = SourceKind.OFFICIAL_CAREERS
    postings: tuple[OfficialPosting, ...]


SourceConfig = Annotated[
    GreenhouseSourceConfig
    | LeverSourceConfig
    | AshbySourceConfig
    | GoogleCareersSourceConfig
    | MicrosoftCareersSourceConfig
    | MicrosoftAiCareersSourceConfig
    | WorkdaySourceConfig
    | AppleCareersSourceConfig
    | AmazonJobsSourceConfig
    | OfficialCareersSourceConfig,
    Field(discriminator="source"),
]

_SOURCE_CONFIG_ADAPTER: TypeAdapter[SourceConfig] = TypeAdapter(SourceConfig)


def parse_source_config(data: JsonObject) -> SourceConfig:
    """Parse an untyped mapping into the correct provider configuration."""

    return _SOURCE_CONFIG_ADAPTER.validate_python(data)
