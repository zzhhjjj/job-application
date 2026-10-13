from typing import Any

import httpx
import pytest

from job_application.domain.models import GreenhouseSourceConfig, WorkplaceType
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.greenhouse import GreenhouseSource


@pytest.mark.asyncio
async def test_greenhouse_maps_public_jobs() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/boards/example/jobs"
        assert request.url.params["content"] == "true"
        return httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "id": 123,
                        "title": "Research Engineer",
                        "first_published": "2026-07-01T12:00:00Z",
                        "updated_at": "2026-07-08T12:00:00Z",
                        "location": {"name": "San Francisco"},
                        "absolute_url": "https://boards.greenhouse.io/example/jobs/123",
                        "content": "&lt;p&gt;Build &amp;amp; operate ML systems.&lt;/p&gt;",
                        "departments": [{"id": 1, "name": "Research"}],
                        "offices": [
                            {"id": 2, "name": "SF", "location": "San Francisco"},
                            {"id": 3, "name": "US", "location": "United States"},
                        ],
                    }
                ],
                "meta": {"total": 1},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await GreenhouseSource(client=client).list_jobs(
            GreenhouseSourceConfig(
                company_name="Example AI",
                board_token="example",
                api_base_url="https://api.example.test",
            )
        )

    assert len(jobs) == 1
    job = jobs[0]
    assert job.external_id == "123"
    assert job.locations == ("San Francisco", "United States")
    assert job.description_text == "Build & operate ML systems."
    assert job.departments == ("Research",)
    assert job.workplace_type is WorkplaceType.UNSPECIFIED
    assert job.published_at is not None


@pytest.mark.asyncio
async def test_greenhouse_rejects_invalid_shape() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        payload: dict[str, Any] = {"jobs": {"not": "a list"}}
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        source = GreenhouseSource(client=client)
        config = GreenhouseSourceConfig(company_name="Example", board_token="example")
        with pytest.raises(SourcePayloadError, match="jobs list"):
            await source.list_jobs(config)
