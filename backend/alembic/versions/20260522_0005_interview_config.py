"""Interview configuration columns (category, difficulty, answer_mode, question_count).

Revision ID: 20260522_0005
Revises: 20260521_0004
Create Date: 2026-05-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260522_0005"
down_revision: Union[str, None] = "20260521_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CATEGORY_VALUES = ("hr", "technical", "behavioral", "dsa", "resume_based", "mixed")
DIFFICULTY_VALUES = ("beginner", "intermediate", "advanced")
ANSWER_MODE_VALUES = ("text", "voice")


def upgrade() -> None:
    bind = op.get_bind()

    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interview_category') THEN "
        f"CREATE TYPE interview_category AS ENUM {CATEGORY_VALUES!r}; "
        "END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interview_difficulty') THEN "
        f"CREATE TYPE interview_difficulty AS ENUM {DIFFICULTY_VALUES!r}; "
        "END IF; END $$;"
    )
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'answer_mode') THEN "
        f"CREATE TYPE answer_mode AS ENUM {ANSWER_MODE_VALUES!r}; "
        "END IF; END $$;"
    )

    op.add_column(
        "interview_sessions",
        sa.Column(
            "category",
            sa.Enum(*CATEGORY_VALUES, name="interview_category", create_type=False),
            nullable=False,
            server_default="mixed",
        ),
    )
    op.add_column(
        "interview_sessions",
        sa.Column(
            "difficulty",
            sa.Enum(*DIFFICULTY_VALUES, name="interview_difficulty", create_type=False),
            nullable=False,
            server_default="intermediate",
        ),
    )
    op.add_column(
        "interview_sessions",
        sa.Column(
            "answer_mode",
            sa.Enum(*ANSWER_MODE_VALUES, name="answer_mode", create_type=False),
            nullable=False,
            server_default="text",
        ),
    )
    op.add_column(
        "interview_sessions",
        sa.Column("question_count", sa.Integer(), nullable=False, server_default="5"),
    )

    op.alter_column("interview_sessions", "category", server_default=None)
    op.alter_column("interview_sessions", "difficulty", server_default=None)
    op.alter_column("interview_sessions", "answer_mode", server_default=None)
    op.alter_column("interview_sessions", "question_count", server_default=None)


def downgrade() -> None:
    op.drop_column("interview_sessions", "question_count")
    op.drop_column("interview_sessions", "answer_mode")
    op.drop_column("interview_sessions", "difficulty")
    op.drop_column("interview_sessions", "category")
    op.execute("DROP TYPE IF EXISTS answer_mode")
    op.execute("DROP TYPE IF EXISTS interview_difficulty")
    op.execute("DROP TYPE IF EXISTS interview_category")
