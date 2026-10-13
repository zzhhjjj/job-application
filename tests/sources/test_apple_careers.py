import json

import httpx
import pytest

from job_application.domain.models import AppleCareersSourceConfig, SourceKind
from job_application.sources.apple_careers import AppleCareersSource


def _page(results: list[dict[str, object]], total: int) -> str:
    hydration = {
        "loaderData": {
            "root": {},
            "search": {"searchResults": results, "totalRecords": total},
        }
    }
    quoted = json.dumps(json.dumps(hydration))
    return (
        f"<html><script>window.__staticRouterHydrationData = JSON.parse({quoted});</script></html>"
    )


def _result(req_id: str, location: str) -> dict[str, object]:
    return {
        "positionId": "200123456",
        "reqId": req_id,
        "postingTitle": "Senior ML Infrastructure Engineer, Training Algorithms",
        "transformedPostingTitle": "senior-ml-infrastructure-engineer-training-algorithms",
        "jobSummary": "Build distributed training infrastructure and improve GPU throughput.",
        "postDateInGMT": "2026-09-20T10:00:00Z",
        "locations": [
            {
                "name": location,
                "stateProvince": "CA" if location == "Cupertino" else "WA",
                "countryName": "United States of America",
            }
        ],
        "team": {"teamName": "Machine Learning Infrastructure"},
    }


@pytest.mark.asyncio
async def test_apple_careers_paginates_and_combines_locations() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/en-us/search"
        assert request.url.params["location"] == "united-states-USA"
        assert request.url.params["team"] == "machine-learning-infrastructure-MLAI-MLI"
        page = int(request.url.params["page"])
        row = _result("200123456-0836", "Cupertino")
        if page == 2:
            row = _result("200123456-3543", "Seattle")
        return httpx.Response(200, text=_page([row], 2))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await AppleCareersSource(client=client).list_jobs(
            AppleCareersSourceConfig(
                company_name="Apple",
                api_base_url="https://jobs.example.test",
            )
        )

    assert len(jobs) == 1
    job = jobs[0]
    assert job.source is SourceKind.APPLE_CAREERS
    assert job.external_id == "200123456"
    assert job.locations == (
        "Cupertino, CA, United States of America",
        "Seattle, WA, United States of America",
    )
    assert "distributed training" in job.description_text
    assert job.teams == ("Machine Learning Infrastructure",)
    assert job.job_url.endswith(
        "/en-us/details/200123456-0836/senior-ml-infrastructure-engineer-training-algorithms"
    )
