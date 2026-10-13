"""Stage-one persistence schema for companies, jobs, snapshots, and matches."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum as PythonEnum
from typing import TypeVar

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from job_application.db.base import Base
from job_application.domain.models import JobStatus, SourceKind, WorkplaceType


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(UTC)


EnumT = TypeVar("EnumT", bound=PythonEnum)


def _enum_values(enum_class: type[EnumT]) -> list[str]:
    return [str(member.value) for member in enum_class]


SOURCE_ENUM = Enum(
    SourceKind,
    name="source_kind",
    native_enum=False,
    values_callable=_enum_values,
    validate_strings=True,
)
JOB_STATUS_ENUM = Enum(
    JobStatus,
    name="job_status",
    native_enum=False,
    values_callable=_enum_values,
    validate_strings=True,
)
WORKPLACE_ENUM = Enum(
    WorkplaceType,
    name="workplace_type",
    native_enum=False,
    values_callable=_enum_values,
    validate_strings=True,
)


preference_companies = Table(
    "preference_companies",
    Base.metadata,
    Column(
        "preference_id",
        String(36),
        ForeignKey("search_preferences.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "company_id",
        String(36),
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Company(Base):
    """A company the user may choose to track."""

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    careers_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    sources: Mapped[list[CompanySource]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    jobs: Mapped[list[Job]] = relationship(back_populates="company")
    search_preferences: Mapped[list[SearchPreference]] = relationship(
        secondary=preference_companies, back_populates="companies"
    )


class CompanySource(Base):
    """Provider-specific board configuration for a company."""

    __tablename__ = "company_sources"
    __table_args__ = (
        UniqueConstraint("company_id", "source", "identifier", name="uq_company_source_board"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source: Mapped[SourceKind] = mapped_column(SOURCE_ENUM, nullable=False)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str | None] = mapped_column(String(32))
    config: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    company: Mapped[Company] = relationship(back_populates="sources")
    jobs: Mapped[list[Job]] = relationship(back_populates="source_record")


class SearchPreference(Base):
    """User-defined rules and thresholds for job discovery."""

    __tablename__ = "search_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tracks: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    title_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    exclude_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    locations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    levels: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    remote_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    minimum_match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    companies: Mapped[list[Company]] = relationship(
        secondary=preference_companies, back_populates="search_preferences"
    )
    match_results: Mapped[list[MatchResult]] = relationship(
        back_populates="preference", cascade="all, delete-orphan"
    )


class Job(Base):
    """Current normalized representation of a public job posting."""

    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source_record_id", "external_id", name="uq_job_source_external_id"),
        Index("ix_jobs_status_last_seen_at", "status", "last_seen_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_record_id: Mapped[str] = mapped_column(
        ForeignKey("company_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    locations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    description_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description_html: Mapped[str | None] = mapped_column(Text)
    employment_type: Mapped[str | None] = mapped_column(String(128))
    workplace_type: Mapped[WorkplaceType] = mapped_column(
        WORKPLACE_ENUM, nullable=False, default=WorkplaceType.UNSPECIFIED
    )
    departments: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    teams: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    job_url: Mapped[str] = mapped_column(Text, nullable=False)
    apply_url: Mapped[str | None] = mapped_column(Text)
    compensation: Mapped[dict[str, object] | None] = mapped_column(JSON)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    status: Mapped[JobStatus] = mapped_column(
        JOB_STATUS_ENUM, nullable=False, default=JobStatus.ACTIVE
    )
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    company: Mapped[Company] = relationship(back_populates="jobs")
    source_record: Mapped[CompanySource] = relationship(back_populates="jobs")
    snapshots: Mapped[list[JobSnapshot]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    match_results: Mapped[list[MatchResult]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class JobSnapshot(Base):
    """Immutable source and normalized payload captured when content changes."""

    __tablename__ = "job_snapshots"
    __table_args__ = (UniqueConstraint("job_id", "content_hash", name="uq_job_snapshot_content"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    job_id: Mapped[str] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    normalized_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    raw_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)

    job: Mapped[Job] = relationship(back_populates="snapshots")


class MatchResult(Base):
    """One explainable rules/LLM evaluation of a job against a preference."""

    __tablename__ = "match_results"
    __table_args__ = (
        Index("ix_match_results_job_preference_created", "job_id", "preference_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    job_id: Mapped[str] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    preference_id: Mapped[str] = mapped_column(
        ForeignKey("search_preferences.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rules_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    matched_track: Mapped[str | None] = mapped_column(String(255))
    reasons: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    concerns: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    recommendation: Mapped[str | None] = mapped_column(String(32))
    llm_model: Mapped[str | None] = mapped_column(String(255))
    prompt_version: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    job: Mapped[Job] = relationship(back_populates="match_results")
    preference: Mapped[SearchPreference] = relationship(back_populates="match_results")


class JobTracking(Base):
    """Dashboard projection and personal decisions, independent of source content."""

    __tablename__ = "job_tracking"
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    availability: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    first_matched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    imported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stage: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    revision: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class SourceHealth(Base):
    """The last attempt and the last successful result are deliberately separate."""

    __tablename__ = "source_health"
    source_id: Mapped[str] = mapped_column(ForeignKey("company_sources.id"), primary_key=True)
    coverage: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="never", nullable=False)
    last_attempt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)
    discovered_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    matched_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class JobEvent(Base):
    """Append-only history; event ids also provide a race-safe read cursor."""

    __tablename__ = "job_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    changes: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)


class DashboardReader(Base):
    """One local user's acknowledged event cursor."""

    __tablename__ = "dashboard_reader"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reviewed_event_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class RefreshBatch(Base):
    """Event boundaries for one locked multi-company refresh, including empty runs."""

    __tablename__ = "refresh_batches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    start_event_id: Mapped[int] = mapped_column(Integer, nullable=False)
    end_event_id: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
