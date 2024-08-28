"""This module holds all the database connection as a Singleton."""
import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from logmgr import logger

DATABASE_URL = "sqlite:///src/database/kiosk.db"

# Create the engine and session factory
try:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    logger.info("Successfully created database connection", f"SQLite -> {DATABASE_URL}")
except sqlalchemy.exc.SQLAlchemyError as ex:
    logger.error("Cannot establish database connection", f"SQLite -> {DATABASE_URL} :: {str(ex)}")

try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    # Import models
    from .models.user import User
    from .models.item import Item
    from .models.transaction import Transaction

    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Successfully created all tables")
except sqlalchemy.exc.SQLAlchemyError as ex:
    logger.error("Cannot bind DB engine to session", f"DB connection failed: {str(ex)}")

class SessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.session = None
        return cls._instance

    def start_session(self):
        if self.session is None:
            self.session = SessionLocal()
            logger.info("Database session started")

    def get_session(self):
        if self.session is None:
            self.start_session()
        return self.session

    def close_session(self):
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