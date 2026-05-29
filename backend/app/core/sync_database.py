"""Synchronous SQLAlchemy session for background resume extraction."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def sync_database_url(async_url: str) -> str:
    return (
        async_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        .replace("postgres+asyncpg://", "postgresql+psycopg2://")
    )


@lru_cache
def _session_factory(database_url: str) -> sessionmaker[Session]:
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=5,
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def sync_db_session() -> Generator[Session, None, None]:
    settings = get_settings()
    db_url = sync_database_url(str(settings.database_url))
    factory = _session_factory(db_url)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
