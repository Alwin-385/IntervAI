"""Resume text extraction fields and status enum update.

Revision ID: 20260521_0004
Revises: 20260519_0003
Create Date: 2026-05-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260521_0004"
down_revision: str | None = "20260519_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("resumes", sa.Column("cleaned_text", sa.Text(), nullable=True))
    op.add_column(
        "resumes",
        sa.Column("extracted_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "resumes",
        sa.Column("text_chunks", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("resumes", sa.Column("extraction_error", sa.Text(), nullable=True))

    op.execute("ALTER TYPE resume_status RENAME TO resume_status_old")
    op.execute(
        "CREATE TYPE resume_status AS ENUM ('queued', 'extracting_resume', 'completed', 'failed')"
    )
    op.execute(
        """
        ALTER TABLE resumes
        ALTER COLUMN status TYPE resume_status
        USING (
            CASE status::text
                WHEN 'uploaded' THEN 'queued'
                WHEN 'processing' THEN 'extracting_resume'
                WHEN 'ready' THEN 'completed'
                WHEN 'failed' THEN 'failed'
                ELSE 'queued'
            END
        )::resume_status
        """
    )
    op.execute("DROP TYPE resume_status_old")


def downgrade() -> None:
    op.execute("ALTER TYPE resume_status RENAME TO resume_status_old")
    op.execute("CREATE TYPE resume_status AS ENUM ('uploaded', 'processing', 'ready', 'failed')")
    op.execute(
        """
        ALTER TABLE resumes
        ALTER COLUMN status TYPE resume_status
        USING (
            CASE status::text
                WHEN 'queued' THEN 'uploaded'
                WHEN 'extracting_resume' THEN 'processing'
                WHEN 'completed' THEN 'ready'
                WHEN 'failed' THEN 'failed'
                ELSE 'uploaded'
            END
        )::resume_status
        """
    )
    op.execute("DROP TYPE resume_status_old")

    op.drop_column("resumes", "extraction_error")
    op.drop_column("resumes", "text_chunks")
    op.drop_column("resumes", "extracted_data")
    op.drop_column("resumes", "cleaned_text")
