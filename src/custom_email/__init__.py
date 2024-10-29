"""
This package manages the email notifications for the kiosk system.
It provides the EmailController class to handle the sending of emails,
and utility functions to format and load the email templates.
"""

# Import classes and functions from email modules
from .email_controller import EmailController
from .email_manager import initialize_email_controller, email_controller

# Export the EmailController class and email manager functions when this package is imported
__all__ = ["EmailController", "initialize_email_controller", "email_controller"]