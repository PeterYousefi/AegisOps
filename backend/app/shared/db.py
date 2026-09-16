"""Database engine, session factory, and declarative base.

The database URL is assembled from individual POSTGRES_* environment parts so
that no full connection string (with credentials) is ever hard-coded. The
engine/session are created lazily so that importing the ORM models does not
require a live database — useful for unit tests and migration autogeneration.
"""

from __future__ import annotations

import datetime as _dt
import uuid
from functools import lru_cache

from enum import Enum as _PyEnum

from sqlalchemy import DateTime, Enum, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    sessionmaker,
)

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def str_enum(enum_cls: type[_PyEnum], length: int = 32) -> Enum:
    """A portable string-enum column type.

    Stores the enum *value* (e.g. "alert"), not its member name, using a
    VARCHAR + CHECK constraint (native_enum=False) for easy migration across
    databases.
    """
    return Enum(
        enum_cls,
        native_enum=False,
        length=length,
        values_callable=lambda e: [member.value for member in e],
    )


class UUIDPrimaryKeyMixin:
    """Adds a string UUID primary key with a generated default."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )


class TimestampMixin:
    """Adds a UTC created_at column (and updated_at where mixed in)."""

    @declared_attr
    def created_at(cls) -> Mapped[_dt.datetime]:  # noqa: N805
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: _dt.datetime.now(_dt.timezone.utc),
        )


def build_database_url() -> str:
    """Assemble the SQLAlchemy database URL from POSTGRES_* settings.

    Reads the individual parts from configuration; never logs the result.
    """
    settings = get_settings()
    return (
        f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )


@lru_cache
def get_engine():
    """Return a cached SQLAlchemy engine.

    Created lazily on first use so that importing models does not open a
    connection.
    """
    return create_engine(build_database_url(), pool_pre_ping=True, future=True)


@lru_cache
def get_sessionmaker() -> sessionmaker:
    """Return a cached session factory bound to the engine."""
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db():
    """FastAPI dependency yielding a database session (closed after the request)."""
    session_factory = get_sessionmaker()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
