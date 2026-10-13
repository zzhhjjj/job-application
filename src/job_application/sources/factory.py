"""Factory for provider adapters."""

from typing import Any

import httpx

from job_application.domain.models import (
    AmazonJobsSourceConfig,
    AppleCareersSourceConfig,
    AshbySourceConfig,
    GoogleCareersSourceConfig,
    GreenhouseSourceConfig,
    LeverSourceConfig,
    MicrosoftAiCareersSourceConfig,
    MicrosoftCareersSourceConfig,
    OfficialCareersSourceConfig,
    SourceConfig,
    WorkdaySourceConfig,
)
from job_application.sources.amazon_jobs import AmazonJobsSource
from job_application.sources.apple_careers import AppleCareersSource
from job_application.sources.ashby import AshbySource
from job_application.sources.base import JobSource
from job_application.sources.google_careers import GoogleCareersSource
from job_application.sources.greenhouse import GreenhouseSource
from job_application.sources.lever import LeverSource
from job_application.sources.microsoft_ai_careers import MicrosoftAiCareersSource
from job_application.sources.microsoft_careers import MicrosoftCareersSource
from job_application.sources.official_careers import OfficialCareersSource
from job_application.sources.workday import WorkdaySource


def create_source(
    config: SourceConfig, *, client: httpx.AsyncClient | None = None
) -> JobSource[Any]:
    """Construct the adapter matching a validated source configuration."""

    if isinstance(config, GreenhouseSourceConfig):
        return GreenhouseSource(client=client)
    if isinstance(config, LeverSourceConfig):
        return LeverSource(client=client)
    if isinstance(config, AshbySourceConfig):
        return AshbySource(client=client)
    if isinstance(config, GoogleCareersSourceConfig):
        return GoogleCareersSource(client=client)
    if isinstance(config, MicrosoftCareersSourceConfig):
        return MicrosoftCareersSource(client=client)
    if isinstance(config, MicrosoftAiCareersSourceConfig):
        return MicrosoftAiCareersSource(client=client)
    if isinstance(config, WorkdaySourceConfig):
        return WorkdaySource(client=client)
    if isinstance(config, AppleCareersSourceConfig):
        return AppleCareersSource(client=client)
    if isinstance(config, AmazonJobsSourceConfig):
        return AmazonJobsSource(client=client)
    if isinstance(config, OfficialCareersSourceConfig):
        return OfficialCareersSource(client=client)
    raise TypeError(f"Unsupported source config: {type(config).__name__}")
