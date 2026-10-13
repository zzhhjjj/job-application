"""Persist dashboard history, personal decisions, and source health."""

import sqlalchemy as sa
from alembic import op

revision = "20260909_0002"
down_revision = "20260709_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_tracking",
        sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id"), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("availability", sa.String(32), nullable=False),
        sa.Column("first_matched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("imported", sa.Boolean(), nullable=False),
        sa.Column("favorite", sa.Boolean(), nullable=False),
        sa.Column("stage", sa.String(32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
    )
    op.create_table(
        "source_health",
        sa.Column(
            "source_id", sa.String(36), sa.ForeignKey("company_sources.id"), primary_key=True
        ),
        sa.Column("coverage", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("last_attempt", sa.DateTime(timezone=True)),
        sa.Column("last_success", sa.DateTime(timezone=True)),
        sa.Column("error", sa.Text()),
        sa.Column("discovered_count", sa.Integer(), nullable=False),
        sa.Column("matched_count", sa.Integer(), nullable=False),
    )
    op.create_table(
        "job_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("changes", sa.JSON(), nullable=False),
    )
    op.create_index("ix_job_events_job_id", "job_events", ["job_id"])
    op.create_table(
        "dashboard_reader",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reviewed_event_id", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("dashboard_reader")
    op.drop_index("ix_job_events_job_id", table_name="job_events")
    op.drop_table("job_events")
    op.drop_table("source_health")
    op.drop_table("job_tracking")
