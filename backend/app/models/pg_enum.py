"""PostgreSQL ENUM columns that persist enum values, not Python member names."""

from enum import Enum

from sqlalchemy.dialects.postgresql import ENUM


def pg_enum(enum_class: type[Enum], name: str, *, create_type: bool = False) -> ENUM:
    """
    Map str Enum members to DB values (e.g. UserRole.CANDIDATE -> 'candidate').

    Without values_callable, asyncpg receives 'CANDIDATE' and Postgres rejects it.
    """
    return ENUM(
        enum_class,
        name=name,
        create_type=create_type,
        values_callable=lambda choices: [item.value for item in choices],
    )
