"""Local SQL-backed job tracking and independently committed source refreshes."""

# ruff: noqa: RUF001 -- Chinese UI messages intentionally use Chinese punctuation.

from __future__ import annotations

import asyncio
import fcntl
import json
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from job_application.config import get_settings
from job_application.dashboard import (
    DASHBOARD_SOURCES,
    DashboardJob,
    DashboardSource,
    _canonicalize_dashboard_job,
    _dashboard_payload,
    match_dashboard_jobs,
    render_dashboard_typescript,
)
from job_application.db.models import (
    Company,
    CompanySource,
    DashboardReader,
    Job,
    JobEvent,
    JobSnapshot,
    JobTracking,
    RefreshBatch,
    SourceHealth,
)
from job_application.db.session import build_engine, build_session_factory
from job_application.domain.models import (
    AmazonJobsSourceConfig,
    AppleCareersSourceConfig,
    DiscoveredJob,
    JobStatus,
    OfficialCareersSourceConfig,
)
from job_application.sources.factory import create_source


def iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.replace(tzinfo=UTC).isoformat()


def coverage(source: DashboardSource) -> str:
    config = source.config
    if isinstance(config, AppleCareersSourceConfig):
        return "Apple 官方 Machine Learning Infrastructure 团队搜索完整分页；美国地点与规则筛选"
    if isinstance(config, AmazonJobsSourceConfig):
        return "Amazon 官方岗位 API 定向关键词搜索完整分页并集；美国地点与规则筛选"
    if isinstance(config, OfficialCareersSourceConfig):
        if any(posting.active_index_url for posting in config.postings):
            return (
                "固定官方岗位页核验；详情页受防护拦截时使用官方岗位索引验证；"
                "不自动发现新岗位；页面内容使用人工维护的摘要"
            )
        return "固定官方岗位页核验；不自动发现新岗位；页面内容使用人工维护的摘要"
    if source.include_external_ids is not None:
        return "完整岗位板抓取，仅跟踪人工选定的岗位 ID"
    if getattr(config, "allow_partial_results", False):
        return "定向关键词搜索的相关性第一页并集，非全量岗位"
    if config.source.value == "microsoft-ai-careers":
        if config.company_name == "MAI Superintelligence":
            return (
                "Microsoft AI 官方岗位页完整抓取；"
                "仅保留明确属于 Superintelligence Team / lab 的岗位"
            )
        return "Microsoft AI 官方岗位页完整抓取；排除已单列的 MAI Superintelligence 岗位"
    if hasattr(config, "max_pages_per_search") and config.source.value == "microsoft-careers":
        return "定向关键词搜索的第一页并集；排除 MAI Superintelligence 与 SCHIE；非全量岗位"
    if getattr(config, "search_texts", ()):
        return "定向关键词搜索完整分页，标题预筛后读取详情；非全站岗位"
    return "公开岗位板完整分页；美国地点与现有 ML Systems 规则筛选"


class RevisionConflict(Exception):
    """Another client saved a newer personal decision."""


class RefreshBusy(Exception):
    """A refresh already owns this database's lock."""


class Tracker:
    def __init__(
        self,
        database_url: str | None = None,
        sources: Sequence[DashboardSource] = DASHBOARD_SOURCES,
    ) -> None:
        self.engine = build_engine(database_url or get_settings().database_url)
        self.sessions = build_session_factory(self.engine)
        self.sources = tuple(sources)
        db_path = self.engine.url.database or "jobs.db"
        self.lock_path = Path(db_path).absolute().with_suffix(".refresh.lock")

    def ensure_sources(self, session: Session) -> dict[str, CompanySource]:
        result = {}
        for spec in self.sources:
            company = session.scalar(
                select(Company).where(Company.name == spec.config.company_name)
            )
            if company is None:
                company = Company(name=spec.config.company_name)
                session.add(company)
                session.flush()
            source = session.scalar(
                select(CompanySource).where(
                    CompanySource.company_id == company.id,
                    CompanySource.identifier == spec.id_prefix,
                )
            )
            if source is None:
                source = CompanySource(
                    company_id=company.id,
                    source=spec.config.source,
                    identifier=spec.id_prefix,
                    config=spec.config.model_dump(mode="json"),
                )
                session.add(source)
                session.flush()
            else:
                source.source = spec.config.source
                source.config = spec.config.model_dump(mode="json")
            health = session.get(SourceHealth, source.id)
            if health is None:
                session.add(SourceHealth(source_id=source.id, coverage=coverage(spec)))
            else:
                health.coverage = coverage(spec)
            result[spec.id_prefix] = source
        if session.get(DashboardReader, 1) is None:
            session.add(DashboardReader(id=1, reviewed_event_id=0))
        session.flush()
        return result

    def bootstrap(self, snapshot: Path) -> None:
        """Import a legacy snapshot once, honestly marked as a JD-less baseline."""
        with self.sessions.begin() as session:
            sources = self.ensure_sources(session)
            if (
                session.scalar(select(func.count()).select_from(JobTracking))
                or not snapshot.exists()
            ):
                return
            text = snapshot.read_text()
            payloads = json.loads(
                text.split("export const jobs: readonly Job[] = ", 1)[1].split(";\n", 1)[0]
            )
            stamp = datetime.strptime(
                text.split('export const snapshotDate = "')[1][:10], "%Y.%m.%d"
            ).replace(tzinfo=UTC)
            by_company = {spec.config.company_name: spec for spec in self.sources}
            for payload in payloads:
                spec = by_company.get(payload["company"])
                if spec is None:
                    continue
                source = sources[spec.id_prefix]
                job = Job(
                    company_id=source.company_id,
                    source_record_id=source.id,
                    external_id=payload["id"].removeprefix(spec.id_prefix + "-"),
                    title=payload["title"],
                    locations=[payload["location"]],
                    job_url=payload["url"],
                    content_hash="legacy",
                    first_seen_at=stamp,
                    last_seen_at=stamp,
                )
                session.add(job)
                session.flush()
                session.add(
                    JobTracking(
                        job_id=job.id, payload=payload, first_matched_at=stamp, imported=True
                    )
                )

    def _event(
        self,
        session: Session,
        job: Job,
        kind: str,
        now: datetime,
        changes: dict[str, Any] | None = None,
    ) -> None:
        session.add(JobEvent(job_id=job.id, kind=kind, occurred_at=now, changes=changes or {}))

    def apply_result(
        self,
        spec: DashboardSource,
        discovered: list[DiscoveredJob],
        *,
        now: datetime | None = None,
        error: str | None = None,
        closed_ids: set[str] | None = None,
        unverified_ids: set[str] | None = None,
    ) -> None:
        now = now or datetime.now(UTC)
        closed_ids, unverified_ids = closed_ids or set(), unverified_ids or set()
        discovered = [_canonicalize_dashboard_job(spec, job) for job in discovered]
        matches = {item.job.external_id: item for item in match_dashboard_jobs(spec, discovered)}
        with self.sessions.begin() as session:
            source = self.ensure_sources(session)[spec.id_prefix]
            health = session.get(SourceHealth, source.id)
            assert health is not None
            health.last_attempt = now
            if error is not None:
                health.status, health.error = "failed", error
                return
            health.status = "partial" if unverified_ids else "ok"
            health.error = (
                "部分官方页面返回 403，保留的岗位尚未重新验证" if unverified_ids else None
            )
            if not unverified_ids:
                health.last_success = now
            health.discovered_count, health.matched_count = len(discovered), len(matches)
            existing = {
                job.external_id: job
                for job in session.scalars(select(Job).where(Job.source_record_id == source.id))
            }
            seen: set[str] = set()
            for found in discovered:
                job = existing.get(found.external_id)
                # Legacy IDs were shortened for display. Reconcile only one exact URL match.
                if job is None:
                    candidates = [
                        j
                        for j in existing.values()
                        if j.content_hash == "legacy" and j.job_url == found.job_url
                    ]
                    if len(candidates) == 1:
                        job = candidates[0]
                        job.external_id = found.external_id
                matched = matches.get(found.external_id)
                if job is None and matched is None:
                    continue
                if job is None and found.external_id in unverified_ids:
                    continue
                created = job is None
                if job is None:
                    job = Job(
                        company_id=source.company_id,
                        source_record_id=source.id,
                        external_id=found.external_id,
                        title=found.title,
                        job_url=found.job_url,
                        content_hash="",
                        first_seen_at=now,
                        last_seen_at=now,
                    )
                    session.add(job)
                    session.flush()
                seen.add(job.id)
                tracking = session.get(JobTracking, job.id)
                previous = tracking.availability if tracking else None
                was_imported = tracking.imported if tracking else False
                if found.external_id in unverified_ids:
                    # A 403 fallback is not a fresh observation or a JD update.
                    if tracking:
                        tracking.availability = "unverified"
                    continue
                changes = {}
                for field in ("title", "locations", "description_text", "job_url", "compensation"):
                    before = getattr(job, field)
                    after = found.normalized_payload()[field]
                    if before != after:
                        changes[field] = {"before": before, "after": after}
                if not created and not was_imported and changes:
                    self._event(session, job, "updated", now, changes)
                job.title, job.locations = found.title, list(found.locations)
                job.description_text, job.description_html = (
                    found.description_text,
                    found.description_html,
                )
                job.job_url, job.apply_url = found.job_url, found.apply_url
                job.compensation = (
                    found.compensation.model_dump(mode="json") if found.compensation else None
                )
                job.departments, job.teams = list(found.departments), list(found.teams)
                job.employment_type, job.workplace_type = (
                    found.employment_type,
                    found.workplace_type,
                )
                job.published_at, job.source_updated_at = (
                    found.published_at,
                    found.source_updated_at,
                )
                job.last_seen_at, job.status = now, JobStatus.ACTIVE
                job.content_hash = found.content_hash()
                if (
                    session.scalar(
                        select(JobSnapshot.id).where(
                            JobSnapshot.job_id == job.id,
                            JobSnapshot.content_hash == job.content_hash,
                        )
                    )
                    is None
                ):
                    session.add(
                        JobSnapshot(
                            job_id=job.id,
                            content_hash=job.content_hash,
                            captured_at=now,
                            normalized_payload=found.normalized_payload(),
                            raw_payload=found.raw_payload,
                        )
                    )
                if tracking is None:
                    assert matched is not None
                    tracking = JobTracking(
                        job_id=job.id, payload=_dashboard_payload(matched), first_matched_at=now
                    )
                    session.add(tracking)
                    self._event(session, job, "new", now)
                tracking.imported = False
                tracking.availability = "active" if matched else "no_match"
                if matched:
                    tracking.payload = _dashboard_payload(matched)
                else:
                    tracking.payload = {
                        **tracking.payload,
                        "title": found.title,
                        "location": " · ".join(found.locations),
                        "url": found.job_url,
                    }
                if previous and previous != tracking.availability:
                    kind = "verified" if previous == "unverified" else "returned"
                    self._event(session, job, kind if matched else "no_match", now)
            for job in existing.values():
                if job.id in seen:
                    continue
                tracking = session.get(JobTracking, job.id)
                if tracking is None:
                    continue
                availability = (
                    "closed"
                    if job.external_id in closed_ids or tracking.availability == "closed"
                    else "not_seen"
                )
                if tracking.availability != availability:
                    tracking.availability = availability
                    self._event(session, job, availability, now)
                if availability == "closed":
                    job.status = JobStatus.CLOSED

    def dashboard(self) -> dict[str, Any]:
        with self.sessions() as session:
            reader = session.get(DashboardReader, 1)
            cursor = reader.reviewed_event_id if reader else 0
            latest = session.scalar(select(func.max(JobEvent.id))) or 0
            batch = session.scalar(select(RefreshBatch).order_by(RefreshBatch.id.desc()).limit(1))
            additions = {
                event.job_id: event.id
                for event in session.scalars(select(JobEvent).where(JobEvent.kind == "new"))
            }
            events = list(session.scalars(select(JobEvent).where(JobEvent.id > cursor)))
            by_job: dict[str, list[str]] = {}
            for event in events:
                by_job.setdefault(event.job_id, []).append(event.kind)
            rows = session.execute(
                select(Job, JobTracking).join(JobTracking, Job.id == JobTracking.job_id)
            ).all()
            jobs = [
                {
                    **tracked.payload,
                    "id": job.id,
                    "availability": tracked.availability,
                    "firstSeenAt": iso(tracked.first_matched_at),
                    "lastSeenAt": iso(job.last_seen_at),
                    "baseline": tracked.imported,
                    "additionGroup": (
                        "latest"
                        if batch
                        and batch.start_event_id
                        < additions.get(job.id, 0)
                        <= (batch.end_event_id if batch.end_event_id is not None else latest)
                        else "earlier"
                        if job.id in additions
                        else None
                    ),
                    "unread": sorted(set(by_job.get(job.id, []))),
                    "personal": {
                        "favorite": tracked.favorite,
                        "stage": tracked.stage,
                        "notes": tracked.notes,
                        "revision": tracked.revision,
                    },
                }
                for job, tracked in rows
            ]
            health_rows = session.execute(
                select(SourceHealth, Company)
                .join(CompanySource, SourceHealth.source_id == CompanySource.id)
                .join(Company, CompanySource.company_id == Company.id)
            ).all()
            sources = [
                {
                    "company": company.name,
                    "status": health.status,
                    "coverage": health.coverage,
                    "lastAttempt": iso(health.last_attempt),
                    "lastSuccess": iso(health.last_success),
                    "error": health.error,
                    "discoveredCount": health.discovered_count,
                    "matchedCount": health.matched_count,
                }
                for health, company in health_rows
            ]
            return {
                "jobs": jobs,
                "sources": sources,
                "latestEventId": latest,
                "reviewedEventId": cursor,
                "latestBatch": {
                    "id": batch.id,
                    "startedAt": iso(batch.started_at),
                    "completedAt": iso(batch.completed_at),
                    "status": batch.status,
                }
                if batch
                else None,
                "refreshing": any(s["status"] == "running" for s in sources),
            }

    def history(self, job_id: str) -> list[dict[str, Any]]:
        with self.sessions() as session:
            if session.get(JobTracking, job_id) is None:
                raise KeyError(job_id)
            return [
                {
                    "id": event.id,
                    "kind": event.kind,
                    "occurredAt": iso(event.occurred_at),
                    "changes": event.changes,
                }
                for event in session.scalars(
                    select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.id.desc())
                )
            ]

    def save_personal(self, job_id: str, revision: int, values: dict[str, Any]) -> dict[str, Any]:
        with self.sessions.begin() as session:
            result = session.execute(
                update(JobTracking)
                .where(JobTracking.job_id == job_id, JobTracking.revision == revision)
                .values(**values, revision=revision + 1)
            )
            if result.rowcount != 1:  # type: ignore[attr-defined]
                if session.get(JobTracking, job_id) is None:
                    raise KeyError(job_id)
                raise RevisionConflict()
            row = session.get(JobTracking, job_id)
            assert row is not None
            return {
                "favorite": row.favorite,
                "stage": row.stage,
                "notes": row.notes,
                "revision": row.revision,
            }

    def mark_reviewed(self, event_id: int) -> None:
        with self.sessions.begin() as session:
            latest = session.scalar(select(func.max(JobEvent.id))) or 0
            session.execute(
                update(DashboardReader)
                .where(DashboardReader.id == 1, DashboardReader.reviewed_event_id < event_id)
                .values(reviewed_event_id=min(event_id, latest))
            )

    def refresh_in_progress(self) -> bool:
        """Check the real process lock and recover abandoned running markers."""
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
            try:
                with self.sessions.begin() as session:
                    session.execute(
                        update(RefreshBatch)
                        .where(RefreshBatch.status == "running")
                        .values(
                            status="interrupted",
                            completed_at=datetime.now(UTC),
                            end_event_id=session.scalar(select(func.max(JobEvent.id))) or 0,
                        )
                    )
                    session.execute(
                        update(SourceHealth)
                        .where(SourceHealth.status == "running")
                        .values(status="failed", error="上次刷新中断，旧数据仍保留")
                    )
                return False
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    async def refresh(self, output: Path, snapshot_date: date) -> list[DashboardJob]:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RefreshBusy("已有刷新正在运行") from exc
            batch_id = None
            finished = False
            try:
                with self.sessions.begin() as session:
                    latest = session.scalar(select(func.max(JobEvent.id))) or 0
                    session.execute(
                        update(RefreshBatch)
                        .where(RefreshBatch.status == "running")
                        .values(
                            status="interrupted",
                            completed_at=datetime.now(UTC),
                            end_event_id=latest,
                        )
                    )
                    batch = RefreshBatch(started_at=datetime.now(UTC), start_event_id=latest)
                    session.add(batch)
                    session.flush()
                    batch_id = batch.id
                    sources = self.ensure_sources(session)
                    for source in sources.values():
                        health = session.get(SourceHealth, source.id)
                        assert health is not None
                        health.status, health.last_attempt = "running", datetime.now(UTC)

                async def fetch(spec: DashboardSource) -> None:
                    try:
                        adapter = create_source(spec.config)
                        discovered = await asyncio.wait_for(
                            adapter.list_jobs(spec.config), timeout=300
                        )
                        self.apply_result(
                            spec,
                            discovered,
                            closed_ids=getattr(adapter, "closed_ids", set()),
                            unverified_ids=getattr(adapter, "unverified_ids", set()),
                        )
                        print(f"{spec.config.company_name}: refreshed", flush=True)
                    except Exception as exc:
                        self.apply_result(spec, [], error=f"{type(exc).__name__}: {exc}"[:2000])
                        print(f"{spec.config.company_name}: failed: {exc}", flush=True)

                await asyncio.gather(*(fetch(spec) for spec in self.sources))
                jobs = self.export_jobs()
                output.parent.mkdir(parents=True, exist_ok=True)
                temporary = output.with_suffix(output.suffix + ".tmp")
                temporary.write_text(render_dashboard_typescript(jobs, snapshot_date))
                temporary.replace(output)
                finished = True
                return jobs
            finally:
                # Interrupted attempts must not masquerade as permanently running.
                with self.sessions.begin() as session:
                    if batch_id is not None:
                        completed_batch = session.get(RefreshBatch, batch_id)
                        assert completed_batch is not None
                        completed_batch.completed_at = datetime.now(UTC)
                        completed_batch.end_event_id = (
                            session.scalar(select(func.max(JobEvent.id))) or 0
                        )
                        failures = session.scalar(
                            select(func.count())
                            .select_from(SourceHealth)
                            .where(SourceHealth.status.in_(["failed", "partial", "running"]))
                        )
                        completed_batch.status = (
                            "interrupted" if not finished else "partial" if failures else "complete"
                        )
                    session.execute(
                        update(SourceHealth)
                        .where(SourceHealth.status == "running")
                        .values(status="failed", error="刷新被中断，保留上次数据")
                    )
                fcntl.flock(lock, fcntl.LOCK_UN)

    def export_jobs(self) -> list[DashboardJob]:
        result = []
        with self.sessions() as session:
            for spec in self.sources:
                rows = session.execute(
                    select(Job, JobTracking)
                    .join(JobTracking, Job.id == JobTracking.job_id)
                    .join(CompanySource, Job.source_record_id == CompanySource.id)
                    .where(
                        CompanySource.identifier == spec.id_prefix,
                        JobTracking.availability.in_(["active", "unverified"]),
                    )
                ).all()
                for job, tracked in rows:
                    from job_application.domain.models import Compensation
                    from job_application.profiles.ml_systems import MatchTrack, RuleMatch

                    payload = tracked.payload
                    found = DiscoveredJob(
                        source=spec.config.source,
                        source_identifier=spec.id_prefix,
                        external_id=job.external_id,
                        company_name=spec.config.company_name,
                        title=str(payload["title"]),
                        locations=(str(payload["location"]),),
                        job_url=str(payload["url"]),
                        compensation=Compensation(summary=str(payload["compensation"]))
                        if payload.get("compensation")
                        else None,
                    )
                    decision = RuleMatch(
                        matched=True,
                        score=int(payload["score"]),
                        tracks=tuple(MatchTrack(t) for t in payload["tracks"]),
                        reasons=tuple(payload["reasons"]),
                    )
                    result.append(
                        DashboardJob(
                            job=found,
                            match=decision,
                            source_label=spec.source_label,
                            id_prefix=spec.id_prefix,
                        )
                    )
        return result
