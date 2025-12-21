"""Database connection helpers.

The application initializes the database once at startup and then provides
SQLAlchemy sessions via a singleton `SessionManager`.

To keep side effects contained, the module stores runtime state in a single
state object instead of multiple module-level globals.
"""

from dataclasses import dataclass
from typing import Any, Optional

import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.logmgr import logger


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class."""


@dataclass
class _DatabaseState:
    config: Optional[dict[str, Any]] = None
    engine: Any = None
    session_local: Any = None


_STATE = _DatabaseState()


def build_database_url(db_config):
    """Build database URL based on configuration."""
    db_type = db_config.get("type", "sqlite").lower()

    if db_type == "sqlite":
        sqlite_config = db_config.get("sqlite", {})
        db_path = sqlite_config.get("path", "src/database/kiosk.db")
        return f"sqlite:///{db_path}"

    if db_type == "postgresql":
        pg_config = db_config.get("postgresql", {})
        host = pg_config.get("host", "localhost")
        port = pg_config.get("port", 5432)
        database = pg_config.get("database", "kiosk")
        username = pg_config.get("username", "")
        password = pg_config.get("password", "")

        return f"postgresql://{username}:{password}@{host}:{port}/{database}"

    raise ValueError(f"Unsupported database type: {db_type}")


def get_engine_kwargs(db_config):
    """Get engine-specific arguments based on database type."""
    db_type = db_config.get("type", "sqlite").lower()

    if db_type == "sqlite":
        return {"connect_args": {"check_same_thread": False}}
    if db_type == "postgresql":
        return {"pool_pre_ping": True, "pool_recycle": 300}
    return {}


def initialize_database(app_config):
    """Initialize database connection with config from main.py"""
    _STATE.config = app_config
    db_config = _STATE.config.get("database", {})

    database_url = build_database_url(db_config)
    engine_kwargs = get_engine_kwargs(db_config)

    try:
        _STATE.engine = create_engine(database_url, **engine_kwargs)
        db_type = db_config.get("type", "sqlite").upper()
        logger.info("Successfully created database connection: %s -> %s", db_type, database_url)

        with _STATE.engine.connect():
            logger.info("Database connection test successful")

    except sqlalchemy.exc.SQLAlchemyError as ex:
        db_type = db_config.get("type", "sqlite").upper()
        logger.error(
            "Cannot establish database connection",
            f"{db_type} -> {database_url} :: {str(ex)}",
        )
        raise

    try:
        _STATE.session_local = sessionmaker(autocommit=False, autoflush=False, bind=_STATE.engine)

        # Import models after engine is successfully created
        from .models.item import Item
        from .models.transaction import Transaction
        from .models.user import User

        _ = [User, Item, Transaction]

        Base.metadata.create_all(bind=_STATE.engine)
        logger.info("Successfully created all tables")

    except sqlalchemy.exc.SQLAlchemyError as ex:
        logger.error("Cannot bind DB engine to session", error=f"DB connection failed: {ex!s}")
        raise
    except (ImportError, OSError) as ex:
        logger.error("Error during table creation", error=f"General error: {ex!s}")
        raise


class SessionManager:
    """Singleton class to manage database sessions."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.session = None
        return cls._instance

    def start_session(self):
        """Start a new database session if not already started."""
        if self.session is None:
            if _STATE.session_local is None:
                raise RuntimeError("Database not initialized. Call initialize_database() first.")
            self.session = _STATE.session_local()
            logger.info("Database session started")

    def get_session(self):
        """Get the current database session."""
        if self.session is None:
            self.start_session()
        return self.session

    def close_session(self):
        """Close the current database session."""
        if self.session is not None:
            logger.info("Closing database session")
            try:
                self.session.close()
                logger.info("Database session closed")
            except sqlalchemy.exc.SQLAlchemyError:
                logger.exception("Error closing database session")
            finally:
                self.session = None


# Use the singleton instance of SessionManager
session_manager = SessionManager()


def get_db():
    """Returns the central db session"""
    return session_manager.get_session()


def get_new_session():
    """Returns a new database session. Caller must close it."""
    if _STATE.session_local is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    return _STATE.session_local()
