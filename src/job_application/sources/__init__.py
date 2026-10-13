"""Public job-board adapters."""

from job_application.sources.ashby import AshbySource
from job_application.sources.base import JobSource
from job_application.sources.factory import create_source
from job_application.sources.greenhouse import GreenhouseSource
from job_application.sources.lever import LeverSource
from job_application.sources.microsoft_ai_careers import MicrosoftAiCareersSource
from job_application.sources.microsoft_careers import MicrosoftCareersSource

__all__ = [
    "AshbySource",
    "GreenhouseSource",
    "JobSource",
    "LeverSource",
    "MicrosoftAiCareersSource",
    "MicrosoftCareersSource",
    "create_source",
]
