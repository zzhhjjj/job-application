"""Tests for the Google Careers public search adapter."""

import json

import httpx
import pytest

from job_application.domain.models import GoogleCareersSourceConfig, SourceKind
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.google_careers import GoogleCareersSource


def _job(
    identifier: str,
    title: str,
    location: str,
    organization: str = "DeepMind",
) -> list[object]:
    qualifications = """
        <h3>Minimum qualifications:</h3>
        <ul><li>Experience with JAX and distributed training.</li></ul>
    """
    about = """
        <p>Build training infrastructure for large-scale model training.</p>
        US: $174,000 - $253,000 (USD) + bonus + equity
    """
    return [
        identifier,
        title,
        f"https://apply.example.test/{identifier}",
        [None, "<ul><li>Optimize training throughput.</li></ul>"],
        [None, qualifications],
        f"projects/example/companies/{organization.casefold()}",
        None,
        organization,
        "en-US",
        [[location, [location], location.split(",")[0], None, None, "US"]],
        [None, about],
        [2],
        [1783000000, 0],
        [1783100000, 0],
        [1783100000, 0],
        [None, ""],
        None,
        None,
        [None, ""],
        [None, qualifications],
    ]


def _page(jobs: list[list[object]] | None, *, total: int, page_size: int | None) -> str:
    payload = json.dumps([jobs, None, total, page_size])
    return (
        '<html><script class="ds:1">'
        "AF_initDataCallback({key: 'ds:1', hash: '2', data:"
        f"{payload}, sideChannel: {{}}}});</script></html>"
    )


@pytest.mark.asyncio
async def test_google_careers_paginates_and_normalizes_embedded_jobs() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/jobs/results"
        assert request.url.params["company"] == "DeepMind"
        assert request.url.params["hl"] == "en-US"
        page = int(request.url.params["page"])
        job = (
            _job("101", "Training Performance Engineer, DeepMind", "Mountain View, CA, USA")
            if page == 1
            else _job("102", "Research Engineer, RL Systems, DeepMind", "London, UK")
        )
        return httpx.Response(200, text=_page([job], total=2, page_size=1))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await GoogleCareersSource(client=client).list_jobs(
            GoogleCareersSourceConfig(
                company_name="Google DeepMind",
                company_filter="DeepMind",
                api_base_url="https://careers.example.test/jobs/results",
            )
        )

    assert [job.external_id for job in jobs] == ["101", "102"]
    first = jobs[0]
    assert first.source is SourceKind.GOOGLE_CAREERS
    assert first.locations == ("Mountain View, CA, USA",)
    assert "Optimize training throughput" in first.description_text
    assert first.departments == ("DeepMind",)
    assert first.apply_url == "https://apply.example.test/101"
    assert first.job_url.endswith("/101-training-performance-engineer-deepmind?company=DeepMind")
    assert first.published_at is not None
    assert first.compensation is not None
    assert first.compensation.min_value == 174000
    assert first.compensation.max_value == 253000


@pytest.mark.asyncio
async def test_google_careers_unions_searches_and_deduplicates_jobs() -> None:
    requested_queries: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        query = request.url.params["q"]
        requested_queries.append(query)
        shared = _job(
            "201",
            "Staff Software Engineer, ML Compilers, TPU",
            "Sunnyvale, CA, USA",
            "Google",
        )
        jobs = [shared]
        if query == "TPU performance":
            jobs.append(
                _job(
                    "202",
                    "Staff Software Engineer, TPU Performance",
                    "Sunnyvale, CA, USA",
                    "Google",
                )
            )
        return httpx.Response(200, text=_page(jobs, total=len(jobs), page_size=20))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await GoogleCareersSource(client=client).list_jobs(
            GoogleCareersSourceConfig(
                company_name="Google",
                company_filter="Google",
                search_texts=("XLA", "TPU performance"),
                api_base_url="https://careers.example.test/jobs/results",
            )
        )

    assert requested_queries == ["XLA", "TPU performance"]
    assert [job.external_id for job in jobs] == ["201", "202"]
    assert all(job.company_name == "Google" for job in jobs)


@pytest.mark.asyncio
async def test_google_careers_accepts_empty_search_results() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["q"] == "PJRT"
        return httpx.Response(200, text=_page([], total=0, page_size=None))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await GoogleCareersSource(client=client).list_jobs(
            GoogleCareersSourceConfig(
                company_name="Google",
                company_filter="Google",
                search_texts=("PJRT",),
                api_base_url="https://careers.example.test/jobs/results",
            )
        )

    assert jobs == []


@pytest.mark.asyncio
async def test_google_careers_accepts_null_jobs_for_empty_search_results() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=_page(None, total=0, page_size=20))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await GoogleCareersSource(client=client).list_jobs(
            GoogleCareersSourceConfig(
                company_name="Google",
                company_filter="Google",
                search_texts=("PJRT",),
                api_base_url="https://careers.example.test/jobs/results",
            )
        )

    assert jobs == []


@pytest.mark.asyncio
async def test_google_careers_can_return_a_bounded_relevance_page() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["page"] == "1"
        job = _job(
            "301",
            "Staff Software Engineer, TPU Performance",
            "Sunnyvale, CA, USA",
            "Google",
        )
        return httpx.Response(200, text=_page([job], total=91, page_size=20))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await GoogleCareersSource(client=client).list_jobs(
            GoogleCareersSourceConfig(
                company_name="Google",
                company_filter="Google",
                search_texts=("TPU software",),
                max_pages=1,
                allow_partial_results=True,
                api_base_url="https://careers.example.test/jobs/results",
            )
        )

    assert [job.external_id for job in jobs] == ["301"]


@pytest.mark.asyncio
async def test_google_careers_can_tolerate_bounded_total_drift() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params["page"])
        if page == 1:
            return httpx.Response(
                200,
                text=_page(
                    [_job("401", "Training Performance Engineer", "Mountain View, CA, USA")],
                    total=2,
                    page_size=1,
                ),
            )
        if page == 2:
            return httpx.Response(
                200,
                text=_page(
                    [_job("402", "Research Engineer, Pretraining", "New York, NY, USA")],
                    total=3,
                    page_size=1,
                ),
            )
        return httpx.Response(200, text=_page([], total=2, page_size=1))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await GoogleCareersSource(client=client).list_jobs(
            GoogleCareersSourceConfig(
                company_name="Google DeepMind",
                company_filter="DeepMind",
                max_total_drift=1,
                api_base_url="https://careers.example.test/jobs/results",
            )
        )

    assert [job.external_id for job in jobs] == ["401", "402"]


@pytest.mark.asyncio
async def test_google_careers_rejects_total_drift_above_configured_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params["page"])
        job = _job(str(500 + page), "Training Performance Engineer", "Seattle, WA, USA")
        return httpx.Response(
            200,
            text=_page([job], total=2 if page == 1 else 4, page_size=1),
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(SourcePayloadError, match="job total changed"):
            await GoogleCareersSource(client=client).list_jobs(
                GoogleCareersSourceConfig(
                    company_name="Google DeepMind",
                    company_filter="DeepMind",
                    max_total_drift=1,
                    api_base_url="https://careers.example.test/jobs/results",
                )
            )


@pytest.mark.asyncio
async def test_google_careers_rejects_missing_embedded_data() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>No search data</html>")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(SourcePayloadError, match="could not locate"):
            await GoogleCareersSource(client=client).list_jobs(
                GoogleCareersSourceConfig(
                    company_name="Google DeepMind",
                    company_filter="DeepMind",
                )
            )


@pytest.mark.asyncio
async def test_google_careers_rejects_duplicate_jobs_across_pages() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        job = _job("101", "Training Performance Engineer, DeepMind", "London, UK")
        return httpx.Response(200, text=_page([job], total=2, page_size=1))

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(SourcePayloadError, match="duplicate job"):
            await GoogleCareersSource(client=client).list_jobs(
                GoogleCareersSourceConfig(
                    company_name="Google DeepMind",
                    company_filter="DeepMind",
                )
            )
