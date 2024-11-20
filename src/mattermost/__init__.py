"""
This package manages the Mattermost notifications and scheduling.
It provides the MattermostController class to interface with Mattermost,
and utility functions to initialize and manage the scheduler.
"""

# Import the MattermostController class from the mattermost_controller module
from .mattermost_controller import MattermostController

# Import the utility functions from the mattermost_manager module
from .mattermost_manager import (
    initialize_mattermost_controller,
    get_mattermost_controller,
    initialize_scheduler,
    send_monthly_summaries,
    get_monthly_summary,
    shutdown_scheduler
)

# Export the MattermostController class and utility functions when this package is imported
__all__ = [
    "MattermostController",
    "initialize_mattermost_controller",
    "get_mattermost_controller",
    "initialize_scheduler",
    "send_monthly_summaries",
    "get_monthly_summary",
    "shutdown_scheduler"
]