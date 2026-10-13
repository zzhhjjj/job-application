from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import func, select, update

from job_application.dashboard import (
    DASHBOARD_SOURCES,
    match_dashboard_jobs,
    render_dashboard_typescript,
)
from job_application.db.models import JobSnapshot, SourceHealth
from job_application.db.session import create_schema
from job_application.domain.models import DiscoveredJob, SourceKind
from job_application.tracking import RefreshBusy, RevisionConflict, Tracker

NOW = datetime(2026, 9, 9, 12, tzinfo=UTC)
SOURCE = DASHBOARD_SOURCES[0]


def found(external_id: str = "1234-full-id", **updates: object) -> DiscoveredJob:
    job = DiscoveredJob(
        source=SourceKind.ASHBY,
        source_identifier="openai",
        company_name="OpenAI",
        external_id=external_id,
        title="Training Performance Engineer",
        locations=("San Francisco, CA",),
        job_url=f"https://example.test/jobs/{external_id}",
        description_text="Build distributed training infrastructure with PyTorch and CUDA.",
    )
    return job.model_copy(update=updates)


@pytest.fixture
def tracker(tmp_path: Path):  # type: ignore[no-untyped-def]
    value = Tracker(f"sqlite:///{tmp_path / 'jobs.db'}", DASHBOARD_SOURCES[:2])
    create_schema(value.engine)
    value.bootstrap(tmp_path / "absent.ts")
    yield value
    value.engine.dispose()


def test_history_is_idempotent_and_content_reversion_keeps_events(tracker: Tracker) -> None:
    original = found()
    tracker.apply_result(SOURCE, [original], now=NOW)
    job_id = tracker.dashboard()["jobs"][0]["id"]
    tracker.apply_result(SOURCE, [original], now=NOW + timedelta(hours=1))
    assert [e["kind"] for e in tracker.history(job_id)] == ["new"]
    changed = found(description_text=original.description_text + " Improve NCCL collectives.")
    tracker.apply_result(SOURCE, [changed], now=NOW + timedelta(hours=2))
    tracker.apply_result(SOURCE, [original], now=NOW + timedelta(hours=3))
    assert [e["kind"] for e in tracker.history(job_id)] == ["updated", "updated", "new"]
    assert (
        tracker.history(job_id)[0]["changes"]["description_text"]["after"]
        == original.description_text
    )
    with tracker.sessions() as session:
        assert session.scalar(select(func.count()).select_from(JobSnapshot)) == 2


def test_personal_decisions_survive_missing_rejected_and_returned_jobs(tracker: Tracker) -> None:
    tracker.apply_result(SOURCE, [found()], now=NOW)
    job_id = tracker.dashboard()["jobs"][0]["id"]
    saved = tracker.save_personal(
        job_id, 0, {"favorite": True, "stage": "applied", "notes": "Referral on Monday"}
    )
    tracker.apply_result(SOURCE, [], now=NOW + timedelta(days=1))
    assert tracker.dashboard()["jobs"][0]["availability"] == "not_seen"
    tracker.apply_result(SOURCE, [found(title="Accountant", description_text="Accounting")])
    assert tracker.dashboard()["jobs"][0]["availability"] == "no_match"
    tracker.apply_result(SOURCE, [found()])
    assert tracker.dashboard()["jobs"][0]["availability"] == "active"
    assert tracker.dashboard()["jobs"][0]["personal"] == saved
    with pytest.raises(RevisionConflict):
        tracker.save_personal(job_id, 0, {"notes": "stale edit"})
    assert tracker.dashboard()["jobs"][0]["personal"]["notes"] == "Referral on Monday"


def test_failure_retains_last_success_and_does_not_mark_jobs_missing(tracker: Tracker) -> None:
    tracker.apply_result(SOURCE, [found()], now=NOW)
    before = tracker.dashboard()
    tracker.apply_result(SOURCE, [], error="TimeoutError", now=NOW + timedelta(days=1))
    after = tracker.dashboard()
    assert after["jobs"] == before["jobs"]
    source = next(s for s in after["sources"] if s["company"] == "OpenAI")
    assert source["status"] == "failed"
    assert source["lastSuccess"] == NOW.isoformat()
    assert source["lastAttempt"] != source["lastSuccess"]
    tracker.apply_result(SOURCE, [found()], now=NOW + timedelta(days=2))
    assert (
        next(s for s in tracker.dashboard()["sources"] if s["company"] == "OpenAI")["error"] is None
    )


def test_closure_requires_explicit_evidence_and_persists_until_seen(tracker: Tracker) -> None:
    tracker.apply_result(SOURCE, [found()], now=NOW)
    tracker.apply_result(SOURCE, [], now=NOW + timedelta(days=1))
    assert tracker.dashboard()["jobs"][0]["availability"] == "not_seen"
    tracker.apply_result(SOURCE, [], closed_ids={found().external_id})
    assert tracker.dashboard()["jobs"][0]["availability"] == "closed"
    tracker.apply_result(SOURCE, [])
    assert tracker.dashboard()["jobs"][0]["availability"] == "closed"
    tracker.apply_result(SOURCE, [found()])
    assert tracker.dashboard()["jobs"][0]["availability"] == "active"


def test_forbidden_fallback_does_not_refresh_jd_or_last_seen(tracker: Tracker) -> None:
    tracker.apply_result(SOURCE, [found()], now=NOW)
    tracker.apply_result(
        SOURCE,
        [found(description_text="old manual summary")],
        now=NOW + timedelta(days=1),
        unverified_ids={found().external_id},
    )
    data = tracker.dashboard()
    job = data["jobs"][0]
    assert job["lastSeenAt"] == NOW.isoformat()
    assert job["availability"] == "unverified"
    assert [e["kind"] for e in tracker.history(job["id"])] == ["new"]
    assert data["sources"][0]["status"] == "partial"
    assert data["sources"][0]["lastSuccess"] == NOW.isoformat()


def test_review_cursor_cannot_hide_concurrent_new_jobs_or_move_backwards(tracker: Tracker) -> None:
    tracker.apply_result(SOURCE, [found("one")])
    observed = tracker.dashboard()["latestEventId"]
    tracker.apply_result(SOURCE, [found("one"), found("two")])
    tracker.mark_reviewed(observed)
    jobs = tracker.dashboard()["jobs"]
    assert sum("new" in job["unread"] for job in jobs) == 1
    tracker.mark_reviewed(0)
    assert tracker.dashboard()["reviewedEventId"] == observed


def test_bootstrap_preserves_identity_and_does_not_invent_new_or_jd_changes(
    tracker: Tracker, tmp_path: Path
) -> None:
    path = tmp_path / "jobs.ts"
    path.write_text(
        render_dashboard_typescript(match_dashboard_jobs(SOURCE, [found()]), date(2026, 8, 25))
    )
    tracker.bootstrap(path)
    baseline = tracker.dashboard()["jobs"][0]
    assert baseline["baseline"] is True
    tracker.save_personal(baseline["id"], 0, {"favorite": True})
    tracker.apply_result(SOURCE, [found()], now=NOW)
    job = tracker.dashboard()["jobs"][0]
    assert job["id"] == baseline["id"]
    assert job["personal"]["favorite"] is True
    assert job["firstSeenAt"] == "2026-08-25T00:00:00+00:00"
    assert tracker.history(job["id"]) == []
    assert job["baseline"] is False


def test_same_short_id_never_collides(tracker: Tracker) -> None:
    tracker.apply_result(SOURCE, [found("1234-alpha"), found("1234-beta")])
    payload = render_dashboard_typescript(tracker.export_jobs(), date(2026, 9, 9))
    assert '"id": "openai-1234-alpha"' in payload
    assert '"id": "openai-1234-beta"' in payload
    assert len({job["id"] for job in tracker.dashboard()["jobs"]}) == 2


@pytest.mark.asyncio
async def test_refresh_lock_and_interrupted_run_recovery(tracker: Tracker, tmp_path: Path) -> None:
    import fcntl

    with tracker.sessions.begin() as session:
        session.execute(update(SourceHealth).values(status="running"))
    with tracker.lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert tracker.refresh_in_progress() is True
        with pytest.raises(RefreshBusy):
            await tracker.refresh(tmp_path / "blocked.ts", date(2026, 9, 9))
        assert not (tmp_path / "blocked.ts").exists()
    assert tracker.refresh_in_progress() is False
    assert all(source["status"] == "failed" for source in tracker.dashboard()["sources"])


@pytest.mark.asyncio
async def test_refresh_commits_other_companies_when_one_source_fails(
    tracker: Tracker, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tracker.apply_result(SOURCE, [found()], now=NOW)

    class Adapter:
        async def list_jobs(self, config):  # type: ignore[no-untyped-def]
            if config.company_name == "OpenAI":
                raise TimeoutError("provider unavailable")
            return [
                found("anthropic").model_copy(
                    update={"company_name": "Anthropic", "source": SourceKind.GREENHOUSE}
                )
            ]

    monkeypatch.setattr("job_application.tracking.create_source", lambda _: Adapter())
    output = tmp_path / "output.ts"
    result = await tracker.refresh(output, date(2026, 9, 9))
    assert len(result) == 2
    assert output.exists()
    data = tracker.dashboard()
    assert {s["company"]: s["status"] for s in data["sources"]} == {
        "OpenAI": "failed",
        "Anthropic": "ok",
    }
    assert (
        next(job for job in data["jobs"] if job["company"] == "OpenAI")["lastSeenAt"]
        == NOW.isoformat()
    )


@pytest.mark.asyncio
async def test_refresh_batches_keep_read_additions_and_rotate_even_without_new_jobs(
    tracker: Tracker, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tracker.sources = (SOURCE,)
    tracker.apply_result(SOURCE, [found("old")], now=NOW)
    postings = [found("old"), found("new")]

    class Adapter:
        async def list_jobs(self, config):  # type: ignore[no-untyped-def]
            return postings

    monkeypatch.setattr("job_application.tracking.create_source", lambda _: Adapter())
    await tracker.refresh(tmp_path / "jobs.ts", date(2026, 9, 26))
    data = tracker.dashboard()
    assert data["latestBatch"]["status"] == "complete"
    groups = {j["url"].rsplit("/", 1)[-1]: j["additionGroup"] for j in data["jobs"]}
    assert groups == {"old": "earlier", "new": "latest"}
    tracker.mark_reviewed(data["latestEventId"])
    assert all(not j["unread"] for j in tracker.dashboard()["jobs"])
    assert [j["additionGroup"] for j in tracker.dashboard()["jobs"]].count("latest") == 1
    new_job = next(j for j in data["jobs"] if j["additionGroup"] == "latest")
    tracker.save_personal(new_job["id"], 0, {"stage": "applied", "notes": "preserved"})
    await tracker.refresh(tmp_path / "jobs.ts", date(2026, 9, 26))
    after = tracker.dashboard()
    assert after["latestBatch"]["id"] > data["latestBatch"]["id"]
    assert all(j["additionGroup"] == "earlier" for j in after["jobs"])
    assert (
        next(j for j in after["jobs"] if j["id"] == new_job["id"])["personal"]["stage"] == "applied"
    )
    # A returned or edited old posting does not become a new addition.
    postings.clear()
    await tracker.refresh(tmp_path / "jobs.ts", date(2026, 9, 26))
    postings.append(found("old", title="Senior Training Performance Engineer"))
    await tracker.refresh(tmp_path / "jobs.ts", date(2026, 9, 26))
    assert all(j["additionGroup"] == "earlier" for j in tracker.dashboard()["jobs"])


@pytest.mark.asyncio
async def test_refreshed_baseline_is_not_an_addition(
    tracker: Tracker, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tracker.sources = (SOURCE,)
    path = tmp_path / "jobs.ts"
    path.write_text(
        render_dashboard_typescript(match_dashboard_jobs(SOURCE, [found()]), date(2026, 8, 25))
    )
    tracker.bootstrap(path)

    class Adapter:
        async def list_jobs(self, config):  # type: ignore[no-untyped-def]
            return [found()]

    monkeypatch.setattr("job_application.tracking.create_source", lambda _: Adapter())
    await tracker.refresh(path, date(2026, 9, 26))
    job = tracker.dashboard()["jobs"][0]
    assert job["baseline"] is False
    assert job["additionGroup"] is None


def test_abandoned_batch_is_recovered_without_losing_additions(tracker: Tracker) -> None:
    from job_application.db.models import RefreshBatch

    with tracker.sessions.begin() as session:
        session.add(RefreshBatch(started_at=NOW, start_event_id=0))
    tracker.apply_result(SOURCE, [found()])
    assert tracker.dashboard()["latestBatch"]["status"] == "running"
    assert tracker.refresh_in_progress() is False
    data = tracker.dashboard()
    assert data["latestBatch"]["status"] == "interrupted"
    assert data["latestBatch"]["completedAt"] is not None
    assert data["jobs"][0]["additionGroup"] == "latest"


async def test_default_refresh_attempts_all_24_companies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from job_application.domain.models import SourceConfig

    attempted = []

    class Adapter:
        async def list_jobs(self, config: SourceConfig) -> list[DiscoveredJob]:
            attempted.append(config.company_name)
            return []

    monkeypatch.setattr("job_application.tracking.create_source", lambda _: Adapter())
    tracker = Tracker(f"sqlite:///{tmp_path / 'all-companies.db'}")
    try:
        create_schema(tracker.engine)
        await tracker.refresh(tmp_path / "jobs.ts", date(2026, 10, 13))
        assert len(attempted) == 24
        assert set(attempted) == {source.config.company_name for source in DASHBOARD_SOURCES}
        assert len(tracker.dashboard()["sources"]) == 24
        assert "companyTiers" not in (tmp_path / "jobs.ts").read_text()
    finally:
        tracker.engine.dispose()
