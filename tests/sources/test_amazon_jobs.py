import json

import httpx
import pytest

from job_application.domain.models import AmazonJobsSourceConfig, SourceKind
from job_application.sources.amazon_jobs import AmazonJobsSource


def _job(identifier: str, title: str) -> dict[str, object]:
    location = {
        "normalizedLocation": "Seattle, Washington, USA",
        "normalizedCountryCode": "USA",
        "type": "ONSITE",
    }
    return {
        "id_icims": identifier,
        "title": title,
        "job_path": f"/en/jobs/{identifier}/training-role",
        "url_next_step": f"https://account.amazon.jobs/apply/{identifier}",
        "locations": [json.dumps(location)],
        "location": "US, WA, Seattle",
        "country_code": "USA",
        "description": "<p>Build distributed training infrastructure for foundation models.</p>",
        "basic_qualifications": "Python and C++",
        "preferred_qualifications": "PyTorch and CUDA",
        "job_category": "Software Development",
        "job_family": "Machine Learning",
        "team": "Amazon AGI",
        "job_schedule_type": "Full time",
        "posted_date": "2026-09-20T10:00:00Z",
        "updated_time": "2026-09-21T10:00:00Z",
    }


@pytest.mark.asyncio
async def test_amazon_jobs_unions_searches_paginates_and_deduplicates() -> None:
    requested: list[tuple[str, int]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        query = request.url.params["base_query"]
        offset = int(request.url.params["offset"])
        requested.append((query, offset))
        if query == "distributed training":
            job = _job("101", "Software Engineer, AI/ML Training")
            if offset == 1:
                job = _job("102", "Machine Learning Engineer, Training Infrastructure")
            return httpx.Response(200, json={"hits": 2, "jobs": [job]})
        return httpx.Response(
            200,
            json={"hits": 1, "jobs": [_job("101", "Software Engineer, AI/ML Training")]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await AmazonJobsSource(client=client).list_jobs(
            AmazonJobsSourceConfig(
                company_name="Amazon",
                api_base_url="https://amazon.example.test",
                search_texts=("distributed training", "ML infrastructure"),
                page_size=1,
            )
        )

    assert requested == [
        ("distributed training", 0),
        ("distributed training", 1),
        ("ML infrastructure", 0),
    ]
    assert [job.external_id for job in jobs] == ["102", "101"]
    first = jobs[0]
    assert first.source is SourceKind.AMAZON_JOBS
    assert first.locations == ("Seattle, Washington, USA", "US, WA, Seattle")
    assert "distributed training infrastructure" in first.description_text
    assert first.teams == ("Amazon AGI",)
    assert first.job_url == "https://amazon.example.test/en/jobs/102/training-role"
