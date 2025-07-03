"""
Messaging Modul für einheitliche Nachrichtenverwaltung.

Stellt eine abstrakte Basisklasse und konkrete Implementierungen
für verschiedene Nachrichtenkanäle bereit.
"""

from .base_messaging_controller import BaseMessagingController
from .email import EmailController, initialize_email_controller, get_email_controller
from .mattermost import MattermostController, initialize_mattermost_controller, get_mattermost_controller
from .messaging_manager import MessagingManager

__all__ = [
    'BaseMessagingController',
    'EmailController', 
    'MattermostController',
    'MessagingManager',
    'initialize_email_controller',
    'get_email_controller',
    'initialize_mattermost_controller',
    'get_mattermost_controller'
]