"""Tests for the Workday public candidate-site adapter."""

import json

import httpx
import pytest

from job_application.domain.models import SourceKind, WorkdaySourceConfig, WorkplaceType
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.workday import WorkdaySource


def _posting(title: str, identifier: str) -> dict[str, object]:
    return {
        "title": title,
        "externalPath": f"/job/Test/{title.replace(' ', '-')}_{identifier}",
        "locationsText": "US, CA, Santa Clara",
        "postedOn": "Posted 2 Days Ago",
        "bulletFields": [identifier],
    }


def _detail(title: str, identifier: str) -> dict[str, object]:
    description = """
        <p>Optimize distributed training performance with CUDA and NCCL.</p>
        <p>The base salary range is 184,000 USD - 287,500 USD for Level 4,
        and 224,000 USD - 356,500 USD for Level 5.</p>
    """
    return {
        "jobPostingInfo": {
            "id": f"internal-{identifier}",
            "title": title,
            "jobDescription": description,
            "location": "US, CA, Santa Clara",
            "additionalLocations": ["US, Remote"],
            "startDate": "2026-07-01",
            "timeType": "Full time",
            "jobReqId": identifier,
            "externalUrl": f"https://careers.example.test/job/{identifier}",
        },
        "hiringOrganization": {"name": "NVIDIA"},
    }


@pytest.mark.asyncio
async def test_workday_paginates_prefilters_and_fetches_details() -> None:
    detail_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            body = json.loads(request.content)
            assert body["searchText"] == "training performance"
            assert body["limit"] == 1
            offset = body["offset"]
            posting = (
                _posting("Senior AI Training Performance Engineer", "JR100")
                if offset == 0
                else _posting("Account Manager", "JR200")
            )
            return httpx.Response(
                200,
                json={"total": 2 if offset == 0 else 0, "jobPostings": [posting]},
            )

        detail_paths.append(request.url.path)
        return httpx.Response(
            200,
            json=_detail("Senior AI Training Performance Engineer", "JR100"),
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await WorkdaySource(client=client).list_jobs(
            WorkdaySourceConfig(
                company_name="NVIDIA",
                tenant="nvidia",
                site="NVIDIAExternalCareerSite",
                api_base_url="https://careers.example.test/wday/cxs/nvidia/site",
                search_texts=("training performance",),
                candidate_title_keywords=("training", "cuda"),
                page_size=1,
            )
        )

    assert len(detail_paths) == 1
    assert len(jobs) == 1
    job = jobs[0]
    assert job.source is SourceKind.WORKDAY
    assert job.external_id == "JR100"
    assert job.locations == ("US, CA, Santa Clara", "US, Remote")
    assert job.workplace_type is WorkplaceType.REMOTE
    assert "distributed training performance" in job.description_text
    assert job.compensation is not None
    assert job.compensation.min_value == 184000
    assert job.compensation.max_value == 356500


@pytest.mark.asyncio
async def test_workday_rejects_invalid_search_shape() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"total": "many", "jobPostings": {}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(SourcePayloadError, match="invalid postings or total"):
            await WorkdaySource(client=client).list_jobs(
                WorkdaySourceConfig(
                    company_name="NVIDIA",
                    tenant="nvidia",
                    site="NVIDIAExternalCareerSite",
                )
            )


@pytest.mark.asyncio
async def test_workday_skips_requisition_only_placeholder() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(
                200,
                json={
                    "total": 2,
                    "jobPostings": [
                        _posting("Training Performance Engineer", "JR100"),
                        {"bulletFields": ["JR200"]},
                    ],
                },
            )
        return httpx.Response(200, json=_detail("Training Performance Engineer", "JR100"))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await WorkdaySource(client=client).list_jobs(
            WorkdaySourceConfig(
                company_name="NVIDIA",
                tenant="nvidia",
                site="NVIDIAExternalCareerSite",
                candidate_title_keywords=("training",),
            )
        )

    assert [job.external_id for job in jobs] == ["JR100"]


@pytest.mark.asyncio
async def test_workday_requires_narrower_search_before_excessive_detail_requests() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        return httpx.Response(
            200,
            json={
                "total": 2,
                "jobPostings": [
                    _posting("Training Performance Engineer", "JR100"),
                    _posting("Distributed Training Engineer", "JR200"),
                ],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(SourcePayloadError, match="exceeding max_details"):
            await WorkdaySource(client=client).list_jobs(
                WorkdaySourceConfig(
                    company_name="NVIDIA",
                    tenant="nvidia",
                    site="NVIDIAExternalCareerSite",
                    max_details=1,
                )
            )
