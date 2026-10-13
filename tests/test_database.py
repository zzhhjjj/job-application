from sqlalchemy import inspect, select

from job_application.db import (
    Company,
    CompanySource,
    Job,
    JobSnapshot,
    SearchPreference,
    build_engine,
    build_session_factory,
    create_schema,
)
from job_application.domain.models import JobStatus, SourceKind, WorkplaceType


def test_schema_and_core_entities_round_trip() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    try:
        create_schema(engine)
        assert set(inspect(engine).get_table_names()) == {
            "companies",
            "company_sources",
            "job_snapshots",
            "jobs",
            "match_results",
            "preference_companies",
            "search_preferences",
            "job_tracking",
            "job_events",
            "source_health",
            "dashboard_reader",
            "refresh_batches",
        }

        session_factory = build_session_factory(engine)
        with session_factory.begin() as session:
            company = Company(name="Example AI", careers_url="https://example.test/careers")
            source = CompanySource(
                company=company,
                source=SourceKind.GREENHOUSE,
                identifier="example",
                config={"board_token": "example"},
            )
            preference = SearchPreference(
                name="ML systems",
                tracks=["ML Systems"],
                title_keywords=["research engineer"],
                companies=[company],
            )
            job = Job(
                company=company,
                source_record=source,
                external_id="123",
                title="Research Engineer",
                locations=["San Francisco"],
                description_text="Build ML systems.",
                workplace_type=WorkplaceType.HYBRID,
                departments=["Research"],
                teams=["Infrastructure"],
                job_url="https://example.test/jobs/123",
                content_hash="a" * 64,
                status=JobStatus.ACTIVE,
            )
            snapshot = JobSnapshot(
                job=job,
                content_hash=job.content_hash,
                normalized_payload={"title": job.title},
                raw_payload={"id": "123"},
            )
            session.add_all([preference, snapshot])

        with session_factory() as session:
            stored = session.scalar(select(Job).where(Job.external_id == "123"))
            assert stored is not None
            assert stored.company.name == "Example AI"
            assert stored.snapshots[0].raw_payload == {"id": "123"}
    finally:
        engine.dispose()
