from datetime import date

from job_application.dashboard import (
    DASHBOARD_SOURCES,
    DashboardJob,
    DashboardSource,
    is_us_job,
    match_dashboard_jobs,
    render_dashboard_typescript,
)
from job_application.domain.models import (
    AshbySourceConfig,
    Compensation,
    DiscoveredJob,
    SourceKind,
)
from job_application.profiles.ml_systems import MatchTrack, RuleMatch


def test_render_dashboard_typescript() -> None:
    job = DiscoveredJob(
        source=SourceKind.ASHBY,
        source_identifier="openai",
        external_id="12345678-abcd",
        company_name="OpenAI",
        title="Training Performance Engineer",
        locations=("San Francisco", "Remote"),
        job_url="https://example.com/job",
        compensation=Compensation(summary="$250K - $445K"),
    )
    decision = RuleMatch(
        matched=True,
        score=20,
        tracks=(MatchTrack.SYSTEMS_PERFORMANCE, MatchTrack.TRAINING_INFRA),
        reasons=("reason one", "reason two", "reason three", "reason four"),
    )

    rendered = render_dashboard_typescript(
        [
            DashboardJob(
                job=job,
                match=decision,
                source_label="Ashby",
                id_prefix="openai",
            )
        ],
        date(2026, 8, 3),
    )

    assert 'export const snapshotDate = "2026.08.03"' in rendered
    assert '"Anthropic" | "SpaceXAI" | "Cursor" | "Google DeepMind"' in rendered
    assert '"Anthropic": 0, "SpaceXAI": 0, "Cursor": 0' in rendered
    assert '"id": "openai-12345678-abcd"' in rendered
    assert '"location": "San Francisco"' in rendered
    assert '"compensation": "$250K - $445K"' in rendered
    assert "reason three" in rendered
    assert "reason four" not in rendered


def test_render_dashboard_uses_greenhouse_primary_location() -> None:
    job = DiscoveredJob(
        source=SourceKind.GREENHOUSE,
        source_identifier="anthropic",
        external_id="123",
        company_name="Anthropic",
        title="Research Engineer, Pretraining",
        locations=(
            "San Francisco, CA | New York City, NY",
            "San Francisco, California, United States",
            "New York, New York, United States",
        ),
        job_url="https://example.com/job",
    )
    decision = RuleMatch(
        matched=True,
        score=12,
        tracks=(MatchTrack.TRAINING_INFRA,),
        reasons=("pretraining",),
    )

    rendered = render_dashboard_typescript(
        [
            DashboardJob(
                job=job,
                match=decision,
                source_label="Greenhouse",
                id_prefix="anthropic",
            )
        ],
        date(2026, 8, 3),
    )

    assert '"location": "San Francisco, CA · New York City, NY"' in rendered
    assert "San Francisco, California, United States" not in rendered


def test_us_location_filter_is_strict_but_allows_mixed_us_roles() -> None:
    def located_job(*locations: str) -> DiscoveredJob:
        return DiscoveredJob(
            source=SourceKind.WORKDAY,
            source_identifier="example",
            external_id="123",
            company_name="Example",
            title="Software Engineer",
            locations=locations,
            job_url="https://example.com/job",
        )

    assert is_us_job(located_job("San Francisco"))
    assert is_us_job(located_job("Palo Alto, California"))
    assert is_us_job(located_job("New York, NY, USA"))
    assert is_us_job(located_job("US, Remote"))
    assert is_us_job(located_job("Germany, Remote", "US, CA, Remote"))
    assert not is_us_job(located_job("London, UK"))
    assert not is_us_job(located_job("China, Shanghai"))
    assert not is_us_job(located_job("Remote"))


def test_render_dashboard_shows_only_us_locations_for_mixed_location_job() -> None:
    job = DiscoveredJob(
        source=SourceKind.GOOGLE_CAREERS,
        source_identifier="DeepMind",
        external_id="123",
        company_name="Google DeepMind",
        title="Research Engineer, Pretraining",
        locations=("London, UK", "Mountain View, CA, USA"),
        job_url="https://example.com/job",
    )
    decision = RuleMatch(
        matched=True,
        score=12,
        tracks=(MatchTrack.TRAINING_INFRA,),
        reasons=("pretraining",),
    )

    rendered = render_dashboard_typescript(
        [
            DashboardJob(
                job=job,
                match=decision,
                source_label="Google Careers",
                id_prefix="deepmind",
            )
        ],
        date(2026, 8, 4),
    )

    assert '"location": "Mountain View, CA, USA"' in rendered
    assert "London, UK" not in rendered


def test_match_dashboard_jobs_uses_company_canonical_job_url() -> None:
    source = DashboardSource(
        config=AshbySourceConfig(company_name="Cursor", job_board_name="cursor"),
        source_label="Ashby",
        id_prefix="cursor",
        canonical_job_url_base="https://cursor.com/careers",
    )
    job = DiscoveredJob(
        source=SourceKind.ASHBY,
        source_identifier="cursor",
        external_id="job-id",
        company_name="Cursor",
        title="Software Engineer, ML Infrastructure",
        locations=("San Francisco",),
        description_text="Build distributed training infrastructure and improve throughput.",
        job_url="https://jobs.ashbyhq.com/cursor/job-id",
        apply_url="https://jobs.ashbyhq.com/cursor/job-id/application",
    )

    [matched] = match_dashboard_jobs(source, [job])

    assert matched.job.job_url == ("https://cursor.com/careers/software-engineer-ml-infrastructure")
    assert matched.job.apply_url == matched.job.job_url


def test_match_dashboard_jobs_allows_reviewed_team_title() -> None:
    source = DashboardSource(
        config=AshbySourceConfig(
            company_name="MAI Superintelligence",
            job_board_name="example",
        ),
        source_label="Microsoft AI Careers",
        id_prefix="mai-superintelligence",
        reviewed_title_keywords=("Data Flywheel Infra",),
        match_threshold=11,
    )
    job = DiscoveredJob(
        source=SourceKind.ASHBY,
        source_identifier="example",
        external_id="200055098",
        company_name="MAI Superintelligence",
        title="Data Flywheel Infra, Frontier Models",
        locations=("Mountain View, United States",),
        description_text="Build data pipelines for pre-training and post-training.",
        job_url="https://example.com/job",
    )

    [matched] = match_dashboard_jobs(source, [job])

    assert matched.match.score == 11
    assert matched.match.tracks == (MatchTrack.TRAINING_INFRA,)
    assert "MAIST" in matched.match.reasons[0]


def test_radixark_uses_current_ashby_board_and_stable_tracking_prefix() -> None:
    from job_application.domain.models import AshbySourceConfig

    source = next(s for s in DASHBOARD_SOURCES if s.config.company_name == "RadixArk")
    assert isinstance(source.config, AshbySourceConfig)
    assert source.config.job_board_name == "radixark"
    assert source.source_label == "Ashby"
    assert source.id_prefix == "radixark"
