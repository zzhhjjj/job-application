import httpx
import pytest

from job_application.domain.models import AshbySourceConfig, WorkplaceType
from job_application.sources.ashby import AshbySource


def _job(*, listed: bool, identifier: str) -> dict[str, object]:
    return {
        "title": "Research Engineer",
        "location": "San Francisco",
        "secondaryLocations": [{"location": "New York"}],
        "department": "Research",
        "team": "ML Systems",
        "isListed": listed,
        "isRemote": True,
        "workplaceType": "Remote",
        "descriptionHtml": "<p>Build reliable AI systems.</p>",
        "descriptionPlain": "Build reliable AI systems.",
        "publishedAt": "2026-07-01T16:21:55.393+00:00",
        "employmentType": "FullTime",
        "jobUrl": f"https://jobs.ashbyhq.com/example/{identifier}",
        "applyUrl": f"https://jobs.ashbyhq.com/example/{identifier}/application",
        "compensation": {
            "compensationTierSummary": "$180K - $240K",
            "scrapeableCompensationSalarySummary": "$180K - $240K",
            "summaryComponents": [
                {
                    "compensationType": "Salary",
                    "interval": "1 YEAR",
                    "currencyCode": "USD",
                    "minValue": 180000,
                    "maxValue": 240000,
                }
            ],
        },
    }


@pytest.mark.asyncio
async def test_ashby_maps_jobs_and_excludes_unlisted_by_default() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/posting-api/job-board/example"
        assert request.url.params["includeCompensation"] == "true"
        return httpx.Response(
            200,
            json={
                "apiVersion": "1",
                "jobs": [
                    _job(listed=True, identifier="public-id"),
                    _job(listed=False, identifier="direct-link-id"),
                ],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await AshbySource(client=client).list_jobs(
            AshbySourceConfig(
                company_name="Example AI",
                job_board_name="example",
                api_base_url="https://api.example.test",
            )
        )

    assert len(jobs) == 1
    job = jobs[0]
    assert job.external_id == "public-id"
    assert job.locations == ("San Francisco", "New York")
    assert job.workplace_type is WorkplaceType.REMOTE
    assert job.compensation is not None
    assert job.compensation.currency == "USD"
    assert job.compensation.max_value == 240000


@pytest.mark.asyncio
async def test_ashby_can_include_unlisted_jobs() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"apiVersion": "1", "jobs": [_job(listed=False, identifier="hidden")]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await AshbySource(client=client).list_jobs(
            AshbySourceConfig(
                company_name="Example",
                job_board_name="example",
                include_unlisted=True,
            )
        )

    assert [job.external_id for job in jobs] == ["hidden"]
