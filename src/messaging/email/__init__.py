"""
Email messaging module.
Contains EmailController and email management functionality.
"""

from .email_controller import EmailController
from .email_manager import get_email_controller, initialize_email_controller

__all__ = ["EmailController", "initialize_email_controller", "get_email_controller"]
