"""Initial job-radar schema.

Revision ID: 20260709_0001
Revises: None
Create Date: 2026-07-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260709_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

source_kind = sa.Enum("greenhouse", "lever", "ashby", name="source_kind", native_enum=False)
job_status = sa.Enum("active", "closed", name="job_status", native_enum=False)
workplace_type = sa.Enum(
    "onsite", "remote", "hybrid", "unspecified", name="workplace_type", native_enum=False
)


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("careers_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_companies"),
        sa.UniqueConstraint("name", name="uq_companies_name"),
    )
    op.create_table(
        "search_preferences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("tracks", sa.JSON(), nullable=False),
        sa.Column("title_keywords", sa.JSON(), nullable=False),
        sa.Column("exclude_keywords", sa.JSON(), nullable=False),
        sa.Column("locations", sa.JSON(), nullable=False),
        sa.Column("levels", sa.JSON(), nullable=False),
        sa.Column("remote_allowed", sa.Boolean(), nullable=False),
        sa.Column("minimum_match_score", sa.Float(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_search_preferences"),
    )
    op.create_table(
        "company_sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("source", source_kind, nullable=False),
        sa.Column("identifier", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=32), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_company_sources_company_id_companies",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_company_sources"),
        sa.UniqueConstraint("company_id", "source", "identifier", name="uq_company_source_board"),
    )
    op.create_index("ix_company_sources_company_id", "company_sources", ["company_id"])
    op.create_table(
        "preference_companies",
        sa.Column("preference_id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_preference_companies_company_id_companies",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["preference_id"],
            ["search_preferences.id"],
            name="fk_preference_companies_preference_id_search_preferences",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("preference_id", "company_id", name="pk_preference_companies"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("source_record_id", sa.String(length=36), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("locations", sa.JSON(), nullable=False),
        sa.Column("description_text", sa.Text(), nullable=False),
        sa.Column("description_html", sa.Text(), nullable=True),
        sa.Column("employment_type", sa.String(length=128), nullable=True),
        sa.Column("workplace_type", workplace_type, nullable=False),
        sa.Column("departments", sa.JSON(), nullable=False),
        sa.Column("teams", sa.JSON(), nullable=False),
        sa.Column("job_url", sa.Text(), nullable=False),
        sa.Column("apply_url", sa.Text(), nullable=True),
        sa.Column("compensation", sa.JSON(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_jobs_company_id_companies",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_record_id"],
            ["company_sources.id"],
            name="fk_jobs_source_record_id_company_sources",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_jobs"),
        sa.UniqueConstraint("source_record_id", "external_id", name="uq_job_source_external_id"),
    )
    op.create_index("ix_jobs_company_id", "jobs", ["company_id"])
    op.create_index("ix_jobs_content_hash", "jobs", ["content_hash"])
    op.create_index("ix_jobs_source_record_id", "jobs", ["source_record_id"])
    op.create_index("ix_jobs_status_last_seen_at", "jobs", ["status", "last_seen_at"])
    op.create_table(
        "job_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("normalized_payload", sa.JSON(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name="fk_job_snapshots_job_id_jobs", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_job_snapshots"),
        sa.UniqueConstraint("job_id", "content_hash", name="uq_job_snapshot_content"),
    )
    op.create_index("ix_job_snapshots_job_id", "job_snapshots", ["job_id"])
    op.create_table(
        "match_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("preference_id", sa.String(length=36), nullable=False),
        sa.Column("rules_passed", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("matched_track", sa.String(length=255), nullable=True),
        sa.Column("reasons", sa.JSON(), nullable=False),
        sa.Column("concerns", sa.JSON(), nullable=False),
        sa.Column("recommendation", sa.String(length=32), nullable=True),
        sa.Column("llm_model", sa.String(length=255), nullable=True),
        sa.Column("prompt_version", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name="fk_match_results_job_id_jobs", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["preference_id"],
            ["search_preferences.id"],
            name="fk_match_results_preference_id_search_preferences",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_match_results"),
    )
    op.create_index("ix_match_results_job_id", "match_results", ["job_id"])
    op.create_index(
        "ix_match_results_job_preference_created",
        "match_results",
        ["job_id", "preference_id", "created_at"],
    )
    op.create_index("ix_match_results_preference_id", "match_results", ["preference_id"])


def downgrade() -> None:
    op.drop_index("ix_match_results_preference_id", table_name="match_results")
    op.drop_index("ix_match_results_job_preference_created", table_name="match_results")
    op.drop_index("ix_match_results_job_id", table_name="match_results")
    op.drop_table("match_results")
    op.drop_index("ix_job_snapshots_job_id", table_name="job_snapshots")
    op.drop_table("job_snapshots")
    op.drop_index("ix_jobs_status_last_seen_at", table_name="jobs")
    op.drop_index("ix_jobs_source_record_id", table_name="jobs")
    op.drop_index("ix_jobs_content_hash", table_name="jobs")
    op.drop_index("ix_jobs_company_id", table_name="jobs")
    op.drop_table("jobs")
    op.drop_table("preference_companies")
    op.drop_index("ix_company_sources_company_id", table_name="company_sources")
    op.drop_table("company_sources")
    op.drop_table("search_preferences")
    op.drop_table("companies")
