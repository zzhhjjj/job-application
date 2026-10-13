import httpx
import pytest

from job_application.domain.models import OfficialCareersSourceConfig, OfficialPosting
from job_application.sources.official_careers import OfficialCareersSource


def posting() -> OfficialPosting:
    return OfficialPosting(
        external_id="role-1",
        title="Machine Learning Performance Engineer",
        locations=("New York, NY, United States",),
        job_url="https://careers.example.test/role-1",
        description_text="Optimize distributed training with CUDA.",
    )


@pytest.mark.asyncio
async def test_official_careers_keeps_active_page() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<h1>Machine Learning Performance Engineer</h1>")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OfficialCareersSource(client=client)
        jobs = await adapter.list_jobs(
            OfficialCareersSourceConfig(company_name="Example", postings=(posting(),))
        )

    assert len(jobs) == 1
    assert jobs[0].external_id == "role-1"
    assert jobs[0].locations == ("New York, NY, United States",)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "body"),
    [(404, "not found"), (200, "This position is no longer available")],
)
async def test_official_careers_drops_closed_or_replaced_page(status: int, body: str) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, text=body)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OfficialCareersSource(client=client)
        jobs = await adapter.list_jobs(
            OfficialCareersSourceConfig(company_name="Example", postings=(posting(),))
        )

    assert jobs == []
    assert adapter.closed_ids == ({"role-1"} if status == 404 else set())


@pytest.mark.asyncio
async def test_official_careers_can_retain_known_bot_blocked_page() -> None:
    blocked_posting = posting().model_copy(update={"retain_on_forbidden": True})

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="Forbidden")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OfficialCareersSource(client=client)
        jobs = await adapter.list_jobs(
            OfficialCareersSourceConfig(company_name="Example", postings=(blocked_posting,))
        )

    assert [job.external_id for job in jobs] == ["role-1"]
    assert adapter.unverified_ids == {"role-1"}


@pytest.mark.asyncio
async def test_official_careers_verifies_bot_blocked_page_from_active_index() -> None:
    active_index_url = "https://careers.example.test/career-sitemap.xml"
    indexed_posting = posting().model_copy(
        update={
            "active_index_url": active_index_url,
            "retain_on_forbidden": True,
        }
    )

    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == active_index_url:
            return httpx.Response(
                200,
                text=(
                    '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/'
                    'schemas/sitemap/0.9"><url><loc>https://careers.example.test/'
                    "role-1/</loc></url></urlset>"
                ),
            )
        return httpx.Response(403, text="Cloudflare challenge")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OfficialCareersSource(client=client)
        jobs = await adapter.list_jobs(
            OfficialCareersSourceConfig(company_name="Example", postings=(indexed_posting,))
        )

    assert [job.external_id for job in jobs] == ["role-1"]
    assert adapter.unverified_ids == set()


@pytest.mark.asyncio
async def test_official_careers_drops_bot_blocked_page_missing_from_active_index() -> None:
    active_index_url = "https://careers.example.test/career-sitemap.xml"
    indexed_posting = posting().model_copy(
        update={
            "active_index_url": active_index_url,
            "retain_on_forbidden": True,
        }
    )

    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == active_index_url:
            return httpx.Response(
                200,
                text=(
                    '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/'
                    'schemas/sitemap/0.9"><url><loc>https://careers.example.test/'
                    "another-role/</loc></url></urlset>"
                ),
            )
        return httpx.Response(403, text="Cloudflare challenge")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OfficialCareersSource(client=client)
        jobs = await adapter.list_jobs(
            OfficialCareersSourceConfig(company_name="Example", postings=(indexed_posting,))
        )

    assert jobs == []
    assert adapter.unverified_ids == set()


@pytest.mark.asyncio
async def test_official_careers_retains_page_when_active_index_is_unavailable() -> None:
    indexed_posting = posting().model_copy(
        update={
            "active_index_url": "https://careers.example.test/career-sitemap.xml",
            "retain_on_forbidden": True,
        }
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text=f"Blocked: {request.url}")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OfficialCareersSource(client=client)
        jobs = await adapter.list_jobs(
            OfficialCareersSourceConfig(company_name="Example", postings=(indexed_posting,))
        )

    assert [job.external_id for job in jobs] == ["role-1"]
    assert adapter.unverified_ids == {"role-1"}
