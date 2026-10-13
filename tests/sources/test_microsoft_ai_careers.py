"""Tests for the official microsoft.ai careers adapter."""

import httpx
import pytest

from job_application.domain.models import MicrosoftAiCareersSourceConfig, SourceKind
from job_application.sources.exceptions import SourcePayloadError
from job_application.sources.microsoft_ai_careers import MicrosoftAiCareersSource


def _listing() -> str:
    return """
    <main id="jobs-container">
      <a href="https://microsoft.ai/careers/job/4402634009/ai-data-platform/">Data</a>
      <a href="/careers/job/4404559009/pre-training/">Pre-Training</a>
      <a href="/careers/job/4402634009/ai-data-platform/">Duplicate</a>
    </main>
    """


def _detail(title: str, job_number: str, description: str) -> str:
    return f"""
    <main>
      <h1><split-text>{title}</split-text></h1>
      <dl>
        <div><dt>Location</dt><dd>Mountain View, United States · London, United Kingdom</dd></div>
        <div><dt>Job Number</dt><dd>{job_number}</dd></div>
        <div><dt>Team</dt><dd>Microsoft AI</dd></div>
        <div><dt>Discipline</dt><dd>Software Engineering</dd></div>
      </dl>
      <div class="wysiwyg greenhouse-wysiwyg m:w-full">
        <p>{description}</p>
        <p>Build distributed training infrastructure and optimize GPU performance.</p>
        <p>USD $188,000 \u2013 $331,200 per year</p>
      </div>
    </main>
    """


@pytest.mark.asyncio
async def test_microsoft_ai_careers_discovers_and_filters_superintelligence_jobs() -> None:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request.url.path)
        if request.url.path == "/careers/":
            return httpx.Response(200, text=_listing())
        if "4402634009" in request.url.path:
            return httpx.Response(
                200,
                text=_detail(
                    "AI Data Platform, Frontier Models",
                    "200055100",
                    "This role is part of Microsoft AI\u2019s Superintelligence Team.",
                ),
            )
        return httpx.Response(
            200,
            text=_detail(
                "Pre-Training Infrastructure",
                "200009146",
                "Microsoft AI is pursuing humanist superintelligence.",
            ),
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await MicrosoftAiCareersSource(client=client).list_jobs(
            MicrosoftAiCareersSourceConfig(
                company_name="MAI Superintelligence",
                api_base_url="https://microsoft.ai",
                required_any_texts=("superintelligence team", "superintelligence lab"),
            )
        )

    assert requests == [
        "/careers/",
        "/careers/job/4402634009/ai-data-platform/",
        "/careers/job/4404559009/pre-training/",
    ]
    assert len(jobs) == 1
    job = jobs[0]
    assert job.source is SourceKind.MICROSOFT_AI_CAREERS
    assert job.company_name == "MAI Superintelligence"
    assert job.external_id == "200055100"
    assert job.locations == (
        "Mountain View, United States",
        "London, United Kingdom",
    )
    assert job.teams == ("Microsoft AI",)
    assert job.departments == ("Software Engineering",)
    assert job.job_url.endswith("/4402634009/ai-data-platform/")
    assert job.apply_url == f"{job.job_url.rstrip('/')}#apply"
    assert job.compensation is not None
    assert job.compensation.min_value == 188000
    assert job.compensation.max_value == 331200


@pytest.mark.asyncio
async def test_microsoft_ai_careers_rejects_empty_listing() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, text="<main />"))
    ) as client:
        with pytest.raises(SourcePayloadError, match="contains no job links"):
            await MicrosoftAiCareersSource(client=client).list_jobs(
                MicrosoftAiCareersSourceConfig(company_name="MAI Superintelligence")
            )


@pytest.mark.asyncio
async def test_microsoft_ai_careers_excludes_superintelligence_from_general_mai() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/careers/":
            return httpx.Response(200, text=_listing())
        if "4402634009" in request.url.path:
            description = "This role is part of Microsoft AI's Superintelligence Team."
        else:
            description = "Microsoft AI is pursuing humanist superintelligence."
        return httpx.Response(
            200,
            text=_detail("Pre-Training Infrastructure", "200009146", description),
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await MicrosoftAiCareersSource(client=client).list_jobs(
            MicrosoftAiCareersSourceConfig(
                company_name="Microsoft AI",
                api_base_url="https://microsoft.ai",
                excluded_any_texts=("superintelligence team",),
            )
        )

    assert [job.external_id for job in jobs] == ["200009146"]


@pytest.mark.parametrize("state", ["California", ""])
@pytest.mark.parametrize("company", ["Microsoft AI", "MAI Superintelligence"])
@pytest.mark.asyncio
async def test_split_location_metadata_keeps_identity_and_team_filter(
    company: str, state: str
) -> None:
    html = _detail(
        "Pre-Training Infrastructure", "200009146", "Join Microsoft AI's Superintelligence Team."
    )
    html = html.replace(
        "<div><dt>Location</dt><dd>Mountain View, United States · "
        "London, United Kingdom</dd></div>",
        f"<div><dt>City</dt><dd>Mountain View</dd></div>"
        f"<div><dt>State</dt><dd>{state}</dd></div>"
        "<div><dt>Country</dt><dd>United States</dd></div>",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=(
                '<a href="/careers/job/4404559009/pre-training/">Job</a>'
                if request.url.path == "/careers/"
                else html
            ),
        )

    is_super = company == "MAI Superintelligence"
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs = await MicrosoftAiCareersSource(client=client).list_jobs(
            MicrosoftAiCareersSourceConfig(
                company_name=company,
                required_any_texts=("superintelligence team",) if is_super else (),
                excluded_any_texts=() if is_super else ("superintelligence team",),
            )
        )
    if not is_super:
        assert jobs == []
    else:
        assert len(jobs) == 1
        assert jobs[0].external_id == "200009146"
        assert jobs[0].locations == (
            "Mountain View, California, United States" if state else "Mountain View, United States",
        )


@pytest.mark.parametrize(
    "metadata, expected",
    [
        ("<dt>City</dt><dd>North America</dd>", "North America"),
        ("<dt>Country</dt><dd>United States</dd>", "United States"),
        (
            "<dt>City</dt><dd>London</dd><dt>Country</dt><dd>United Kingdom</dd>",
            "London, United Kingdom",
        ),
        ("", None),
        ("<dt>City</dt><dd> </dd><dt>Country</dt><dd> </dd>", None),
    ],
)
def test_sparse_or_missing_location(metadata: str, expected: str | None) -> None:
    html = _detail("Engineer", "123", "Build distributed training infrastructure.")
    html = html.replace(
        "<dt>Location</dt><dd>Mountain View, United States · London, United Kingdom</dd>",
        metadata,
    )
    source = MicrosoftAiCareersSource()
    config = MicrosoftAiCareersSourceConfig(company_name="Microsoft AI")
    url = "https://microsoft.ai/careers/job/456/engineer/"
    if expected is None:
        with pytest.raises(SourcePayloadError, match="missing Location or City/State/Country"):
            source._parse_job(config, "456", url, html)
    else:
        assert source._parse_job(config, "456", url, html).locations == (expected,)


def test_legacy_multilocation_takes_precedence_over_split_metadata() -> None:
    html = _detail("Engineer", "123", "Training infrastructure.")
    html = html.replace(
        "</dl>", "<dt>City</dt><dd>Seattle</dd><dt>Country</dt><dd>United States</dd></dl>"
    )
    job = MicrosoftAiCareersSource()._parse_job(
        MicrosoftAiCareersSourceConfig(company_name="Microsoft AI"),
        "456",
        "https://microsoft.ai/careers/job/456/engineer/",
        html,
    )
    assert job.locations == ("Mountain View, United States", "London, United Kingdom")
