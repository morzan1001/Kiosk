"""
This package provides database connectivity and models for the Kiosk application.

It includes:
- Connection setup
- User, Item, and Transaction models
"""

from src.database.connection import SessionManager, get_db

# Models
from src.database.models.user import User
from src.database.models.item import Item 
from src.database.models.transaction import Transaction

# Export classes and functions when this package is imported
__all__ = ["SessionManager", "get_db", "User", "Item", "Transaction"]