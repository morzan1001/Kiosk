"""This module holds all the database connection as a Singleton."""

import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.logmgr import logger

Base = declarative_base()

CONFIG = None
ENGINE = None
SESSION_LOCAL = None


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
    global CONFIG, ENGINE, SESSION_LOCAL

    CONFIG = app_config
    db_config = CONFIG.get("database", {})

    database_url = build_database_url(db_config)
    engine_kwargs = get_engine_kwargs(db_config)

    try:
        ENGINE = create_engine(database_url, **engine_kwargs)
        db_type = db_config.get("type", "sqlite").upper()
        logger.info(
            "Successfully created database connection", f"{db_type} -> {database_url}"
        )

        with ENGINE.connect():
            logger.info("Database connection test successful")

    except sqlalchemy.exc.SQLAlchemyError as ex:
        db_type = db_config.get("type", "sqlite").upper()
        logger.error(
            "Cannot establish database connection",
            f"{db_type} -> {database_url} :: {str(ex)}",
        )
        raise

    try:
        SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

        # Import models after engine is successfully created
        from .models.item import Item
        from .models.transaction import Transaction
        from .models.user import User

        _ = [User, Item, Transaction]

        Base.metadata.create_all(bind=ENGINE)
        logger.info("Successfully created all tables")

    except sqlalchemy.exc.SQLAlchemyError as ex:
        logger.error(
            "Cannot bind DB engine to session", f"DB connection failed: {str(ex)}"
        )
        raise
    except Exception as ex:
        logger.error("Error during table creation", f"General error: {str(ex)}")
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
            if SESSION_LOCAL is None:
                raise RuntimeError(
                    "Database not initialized. Call initialize_database() first."
                )
            self.session = SESSION_LOCAL()
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
            except Exception as e:
                logger.error(f"Error closing database session: {e}")
            finally:
                self.session = None


# Use the singleton instance of SessionManager
session_manager = SessionManager()


def get_db():
    """Returns the central db session"""
    return session_manager.get_session()


def get_new_session():
    """Returns a new database session. Caller must close it."""
    if SESSION_LOCAL is None:
        raise RuntimeError(
            "Database not initialized. Call initialize_database() first."
        )
    return SESSION_LOCAL()
