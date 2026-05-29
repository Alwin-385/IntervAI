"""background_jobs table for Phase 18."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260527_0008"
down_revision: Union[str, None] = "20260524_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


JOB_TYPE_VALUES = (
    "resume_extraction",
    "resume_analysis",
    "question_generation",
    "transcription",
    "answer_evaluation",
    "roadmap_generation",
)
JOB_STATUS_VALUES = (
    "pending",
    "running",
    "retrying",
    "completed",
    "failed",
    "cancelled",
)

background_job_type = postgresql.ENUM(
    *JOB_TYPE_VALUES,
    name="background_job_type",
    create_type=False,
)
background_job_status = postgresql.ENUM(
    *JOB_STATUS_VALUES,
    name="background_job_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'background_job_type') THEN "
        f"CREATE TYPE background_job_type AS ENUM {JOB_TYPE_VALUES!r}; "
        "END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'background_job_status') THEN "
        f"CREATE TYPE background_job_status AS ENUM {JOB_STATUS_VALUES!r}; "
        "END IF; END $$;"
    )

    op.create_table(
        "background_jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("job_type", background_job_type, nullable=False),
        sa.Column(
            "status",
            background_job_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("celery_task_id", sa.String(length=255), nullable=True),
        sa.Column("resource_type", sa.String(length=64), nullable=True),
        sa.Column("resource_id", sa.UUID(), nullable=True),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("progress_step", sa.String(length=64), nullable=True),
        sa.Column("progress_message", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_background_jobs_user_id", "background_jobs", ["user_id"])
    op.create_index("ix_background_jobs_status", "background_jobs", ["status"])
    op.create_index("ix_background_jobs_job_type", "background_jobs", ["job_type"])
    op.create_index(
        "ix_background_jobs_resource",
        "background_jobs",
        ["resource_type", "resource_id"],
    )
    op.create_index(
        "ix_background_jobs_celery_task_id",
        "background_jobs",
        ["celery_task_id"],
    )


def downgrade() -> None:
    op.drop_table("background_jobs")
    op.execute("DROP TYPE IF EXISTS background_job_status")
    op.execute("DROP TYPE IF EXISTS background_job_type")
