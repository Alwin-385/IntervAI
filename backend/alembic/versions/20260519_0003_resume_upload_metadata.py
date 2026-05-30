"""Add resume upload metadata columns.

Revision ID: 20260519_0003
Revises: 20260519_0002
Create Date: 2026-05-19

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260519_0003"
down_revision: str | None = "20260519_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "resumes",
        sa.Column("storage_key", sa.String(length=1024), nullable=True),
    )
    op.add_column(
        "resumes",
        sa.Column(
            "mime_type", sa.String(length=128), server_default="application/pdf", nullable=False
        ),
    )
    op.add_column(
        "resumes",
        sa.Column("file_size_bytes", sa.BigInteger(), server_default="0", nullable=False),
    )
    op.execute("UPDATE resumes SET storage_key = storage_path WHERE storage_key IS NULL")
    op.alter_column("resumes", "storage_key", nullable=False)


def downgrade() -> None:
    op.drop_column("resumes", "file_size_bytes")
    op.drop_column("resumes", "mime_type")
    op.drop_column("resumes", "storage_key")
