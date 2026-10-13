"""Errors raised by job-board adapters."""

from job_application.domain.models import SourceKind


class SourceError(RuntimeError):
    """Base class for source failures safe to report to callers."""

    def __init__(self, source: SourceKind, message: str) -> None:
        self.source = source
        super().__init__(f"{source.value}: {message}")


class SourceRequestError(SourceError):
    """Network, timeout, or HTTP failure while reading a source."""


class SourcePayloadError(SourceError):
    """The provider returned JSON that does not match its public contract."""
