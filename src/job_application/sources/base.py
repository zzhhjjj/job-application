"""Common asynchronous interface and HTTP behavior for job sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, ClassVar, Generic, TypeVar

import httpx

from job_application.config import get_settings
from job_application.domain.models import BaseSourceConfig, DiscoveredJob, SourceKind
from job_application.sources.exceptions import SourcePayloadError, SourceRequestError

ConfigT = TypeVar("ConfigT", bound=BaseSourceConfig)


class JobSource(ABC, Generic[ConfigT]):
    """Interface implemented by every job provider.

    A caller may inject an ``httpx.AsyncClient`` for connection reuse and testing.
    Without one, the adapter owns a short-lived client for each ``list_jobs`` call.
    """

    kind: ClassVar[SourceKind]

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        timeout_seconds: float | None = None,
        user_agent: str | None = None,
    ) -> None:
        settings = get_settings()
        self._client = client
        self._timeout_seconds = timeout_seconds or settings.http_timeout_seconds
        self._user_agent = user_agent or settings.http_user_agent

    @abstractmethod
    async def list_jobs(self, config: ConfigT) -> list[DiscoveredJob]:
        """Fetch all currently visible jobs for one configured company board."""

    @asynccontextmanager
    async def client_session(self) -> AsyncIterator[httpx.AsyncClient]:
        """Yield an injected client or manage a temporary one."""

        if self._client is not None:
            yield self._client
            return

        async with httpx.AsyncClient(
            timeout=self._timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": self._user_agent, "Accept": "application/json"},
        ) as client:
            yield client

    async def get_json(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        params: dict[str, str | int] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """GET JSON and translate transport details into stable domain errors."""

        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SourceRequestError(self.kind, f"request failed for {url}: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise SourcePayloadError(self.kind, f"non-JSON response from {url}") from exc

    async def get_text(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        params: dict[str, str | int] | None = None,
        headers: dict[str, str] | None = None,
    ) -> str:
        """GET text and translate transport details into stable domain errors."""

        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SourceRequestError(self.kind, f"request failed for {url}: {exc}") from exc
        return response.text

    async def post_json(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        payload: dict[str, Any],
    ) -> Any:
        """POST JSON and translate transport and response errors."""

        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SourceRequestError(self.kind, f"request failed for {url}: {exc}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise SourcePayloadError(self.kind, f"non-JSON response from {url}") from exc
