"""Explicit engine and session construction without import-time side effects."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from job_application.db.base import Base


def build_engine(database_url: str, *, echo: bool = False) -> Engine:
    """Construct an engine for the supplied SQLAlchemy URL."""

    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, echo=echo, connect_args=connect_args)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Construct a session factory with safe transaction defaults."""

    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_schema(engine: Engine) -> None:
    """Create all tables for local development and tests.

    Production and long-lived databases should use Alembic migrations instead.
    """

    # Import model modules before accessing metadata.
    from job_application.db import models as _models  # noqa: F401

    Base.metadata.create_all(engine)
