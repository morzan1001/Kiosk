"""
Mattermost messaging module.
Contains MattermostController and mattermost management functionality.
"""

from .mattermost_controller import MattermostController
from .mattermost_manager import initialize_mattermost_controller, get_mattermost_controller

__all__ = [
    'MattermostController',
    'initialize_mattermost_controller',
    'get_mattermost_controller'
]
