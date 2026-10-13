"""Tests for the Microsoft Eightfold public careers adapter."""

import httpx
import pytest

from job_application.domain.models import (
    MicrosoftCareersSourceConfig,
    SourceKind,
    WorkplaceType,
)
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.microsoft_careers import MicrosoftCareersSource


def _position(identifier: int, title: str) -> dict[str, object]:
    return {
        "id": identifier,
        "displayJobId": f"REQ{identifier}",
        "name": title,
        "locations": ["United States, Washington, Redmond"],
        "postedTs": 1_774_029_648,
        "department": "Software Engineering",
        "positionUrl": f"/careers/job/{identifier}",
    }


def _detail(identifier: int, title: str) -> dict[str, object]:
    description = """
        <p>Microsoft AI is looking for a Member of Technical Staff.</p>
        <p>Design distributed training infrastructure, profile GPU performance,
        and optimize CUDA and NCCL collective communication.</p>
        <p>The typical base pay range is USD $142,800 - $274,800 per year.
        The Bay Area range is USD $188,000 - $331,200 per year.</p>
    """
    return {
        "status": 200,
        "data": {
            "id": identifier,
            "displayJobId": f"REQ{identifier}",
            "name": title,
            "locations": ["United States, Washington, Redmond"],
            "postedTs": 1_774_029_648,
            "department": "Software Engineering",
            "jobDescription": description,
            "workLocationOption": "onsite",
            "efcustomTextEmploymentType": ["Full-Time"],
            "publicUrl": f"https://careers.example.test/careers/job/{identifier}",
        },
    }


@pytest.mark.asyncio
async def test_microsoft_careers_unions_queries_prefilters_and_fetches_details() -> None:
    detail_requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert "Mozilla/5.0" in request.headers["user-agent"]
        if request.url.path.endswith("/search"):
            assert request.url.params["domain"] == "microsoft.com"
            assert request.url.params["sort_by"] == "relevance"
            return httpx.Response(
                200,
                json={
                    "status": 200,
                    "data": {
                        "count": 2,
                        "positions": [
                            _position(100, "Pre-Training Infrastructure"),
                            _position(200, "Account Manager"),
                        ],
                    },
                },
            )

        detail_requests.append(request.url.params["position_id"])
        assert request.headers["referer"].endswith("/careers/job/100")
        return httpx.Response(200, json=_detail(100, "Pre-Training Infrastructure"))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await MicrosoftCareersSource(client=client).list_jobs(
            MicrosoftCareersSourceConfig(
                company_name="Microsoft AI",
                domain="microsoft.com",
                api_base_url="https://careers.example.test",
                search_texts=("training infrastructure", "distributed training"),
                candidate_title_keywords=("training",),
                required_description_text="Microsoft AI",
            )
        )

    assert detail_requests == ["100"]
    assert len(jobs) == 1
    job = jobs[0]
    assert job.source is SourceKind.MICROSOFT_CAREERS
    assert job.external_id == "REQ100"
    assert job.locations == ("United States, Washington, Redmond",)
    assert job.workplace_type is WorkplaceType.ONSITE
    assert job.employment_type == "Full-Time"
    assert "distributed training infrastructure" in job.description_text
    assert job.compensation is not None
    assert job.compensation.min_value == 142800
    assert job.compensation.max_value == 331200


@pytest.mark.asyncio
async def test_microsoft_careers_rejects_invalid_search_shape() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": 200, "data": {"count": "many"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(SourcePayloadError, match="invalid positions or count"):
            await MicrosoftCareersSource(client=client).list_jobs(
                MicrosoftCareersSourceConfig(company_name="Microsoft AI")
            )


@pytest.mark.asyncio
async def test_microsoft_careers_applies_organization_text_filter() -> None:
    detail = _detail(100, "Pre-Training Infrastructure")
    detail["data"]["jobDescription"] = "<p>Azure Core infrastructure role.</p>"  # type: ignore[index]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/search"):
            return httpx.Response(
                200,
                json={
                    "status": 200,
                    "data": {
                        "count": 1,
                        "positions": [_position(100, "Pre-Training Infrastructure")],
                    },
                },
            )
        return httpx.Response(200, json=detail)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await MicrosoftCareersSource(client=client).list_jobs(
            MicrosoftCareersSourceConfig(
                company_name="Microsoft AI",
                required_description_text="Microsoft AI",
            )
        )

    assert jobs == []


@pytest.mark.asyncio
async def test_microsoft_careers_excludes_other_organizations() -> None:
    detail = _detail(100, "Pre-Training Infrastructure")
    detail["data"]["jobDescription"] += (  # type: ignore[index,operator]
        "<p>This role is part of Microsoft AI's Superintelligence Team.</p>"
    )

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/search"):
            return httpx.Response(
                200,
                json={
                    "status": 200,
                    "data": {
                        "count": 1,
                        "positions": [_position(100, "Pre-Training Infrastructure")],
                    },
                },
            )
        return httpx.Response(200, json=detail)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await MicrosoftCareersSource(client=client).list_jobs(
            MicrosoftCareersSourceConfig(
                company_name="Microsoft AI",
                required_description_text="Microsoft AI",
                excluded_description_texts=("Superintelligence Team", "SCHIE"),
            )
        )

    assert jobs == []
