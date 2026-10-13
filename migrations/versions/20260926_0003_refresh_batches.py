"""Track refresh boundaries without changing existing history or personal decisions."""

import sqlalchemy as sa
from alembic import op

revision = "20260926_0003"
down_revision = "20260909_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "refresh_batches",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("start_event_id", sa.Integer(), nullable=False),
        sa.Column("end_event_id", sa.Integer()),
        sa.Column("status", sa.String(32), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("refresh_batches")
