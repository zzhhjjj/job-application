import httpx
import pytest

from job_application.domain.models import LeverSourceConfig, WorkplaceType
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.lever import LeverSource


def _posting(identifier: str, title: str) -> dict[str, object]:
    return {
        "id": identifier,
        "text": title,
        "categories": {
            "location": "San Francisco",
            "allLocations": ["San Francisco", "Remote"],
            "commitment": "Full-time",
            "department": "Engineering",
            "team": "ML Platform",
        },
        "description": "<p>Build training infrastructure.</p>",
        "descriptionPlain": "Build training infrastructure.",
        "hostedUrl": f"https://jobs.lever.co/example/{identifier}",
        "applyUrl": f"https://jobs.lever.co/example/{identifier}/apply",
        "workplaceType": "hybrid",
        "createdAt": 1_751_371_200_000,
        "salaryRange": {
            "currency": "USD",
            "interval": "year",
            "min": 180000,
            "max": 250000,
        },
        "salaryDescriptionPlain": "$180K-$250K",
    }


@pytest.mark.asyncio
async def test_lever_paginates_and_maps_jobs() -> None:
    requested_skips: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v0/postings/example"
        skip = int(request.url.params["skip"])
        requested_skips.append(skip)
        payload = [_posting("one", "Research Engineer"), _posting("two", "ML Engineer")]
        if skip == 2:
            payload = [_posting("three", "Systems Engineer")]
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await LeverSource(client=client).list_jobs(
            LeverSourceConfig(
                company_name="Example AI",
                site="example",
                api_base_url="https://api.example.test",
                page_size=2,
            )
        )

    assert requested_skips == [0, 2]
    assert [job.external_id for job in jobs] == ["one", "two", "three"]
    assert jobs[0].workplace_type is WorkplaceType.HYBRID
    assert jobs[0].compensation is not None
    assert jobs[0].compensation.min_value == 180000
    assert jobs[0].published_at is not None


@pytest.mark.asyncio
async def test_lever_detects_repeated_pagination_page() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[_posting("same", "Engineer")])

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        source = LeverSource(client=client)
        config = LeverSourceConfig(
            company_name="Example",
            site="example",
            api_base_url="https://api.example.test",
            page_size=1,
        )
        with pytest.raises(SourcePayloadError, match="repeated a page"):
            await source.list_jobs(config)
