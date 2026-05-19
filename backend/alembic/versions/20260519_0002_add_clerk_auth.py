"""Add Clerk authentication fields to users.

Revision ID: 20260519_0002
Revises: 20260519_0001
Create Date: 2026-05-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_0002"
down_revision: Union[str, None] = "20260519_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("clerk_id", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(length=1024), nullable=True))
    op.alter_column("users", "hashed_password", existing_type=sa.String(length=255), nullable=True)
    op.create_index("ix_users_clerk_id", "users", ["clerk_id"], unique=False)
    op.create_unique_constraint("uq_users_clerk_id", "users", ["clerk_id"])


def downgrade() -> None:
    op.drop_constraint("uq_users_clerk_id", "users", type_="unique")
    op.drop_index("ix_users_clerk_id", table_name="users")
    op.alter_column("users", "hashed_password", existing_type=sa.String(length=255), nullable=False)
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "clerk_id")
