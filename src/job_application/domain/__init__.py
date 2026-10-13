"""Provider-independent domain types."""

from job_application.domain.models import (
    AshbySourceConfig,
    Compensation,
    DiscoveredJob,
    GreenhouseSourceConfig,
    JobStatus,
    LeverRegion,
    LeverSourceConfig,
    MicrosoftAiCareersSourceConfig,
    MicrosoftCareersSourceConfig,
    SourceConfig,
    SourceKind,
    WorkplaceType,
    parse_source_config,
)

__all__ = [
    "AshbySourceConfig",
    "Compensation",
    "DiscoveredJob",
    "GreenhouseSourceConfig",
    "JobStatus",
    "LeverRegion",
    "LeverSourceConfig",
    "MicrosoftAiCareersSourceConfig",
    "MicrosoftCareersSourceConfig",
    "SourceConfig",
    "SourceKind",
    "WorkplaceType",
    "parse_source_config",
]
