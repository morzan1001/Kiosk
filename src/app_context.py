"""
Application Context for Dependency Injection.
Manages all application-wide controllers and services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.lock.lock import GPIOController
    from src.messaging.email.email_controller import EmailController
    from src.messaging.mattermost.mattermost_controller import MattermostController
    from src.sounds.sound_controller import SoundController


@dataclass
class AppContext:
    """
    Central application context that holds all controllers and services.
    Use this instead of global variables for dependency injection.
    """

    gpio_controller: Optional[GPIOController] = None
    sound_controller: Optional[SoundController] = None
    email_controller: Optional[EmailController] = None
    mattermost_controller: Optional[MattermostController] = None
    _scheduler_email: Optional[object] = field(default=None, repr=False)
    _scheduler_mattermost: Optional[object] = field(default=None, repr=False)

    def cleanup(self) -> None:
        """Cleanup all controllers and resources."""
        if self.sound_controller:
            self.sound_controller.stop()
            self.sound_controller.join()
            self.sound_controller = None

        if self.gpio_controller:
            self.gpio_controller.cleanup()
            self.gpio_controller = None

        if self._scheduler_email:
            self._scheduler_email.shutdown()
            self._scheduler_email = None

        if self._scheduler_mattermost:
            self._scheduler_mattermost.shutdown()
            self._scheduler_mattermost = None

        if self.email_controller:
            self.email_controller.stop()
            self.email_controller = None

        if self.mattermost_controller:
            self.mattermost_controller.stop()
            self.mattermost_controller = None


# Global application context instance
_app_context: Optional[AppContext] = None


def get_app_context() -> AppContext:
    """Get the global application context instance."""
    global _app_context
    if _app_context is None:
        _app_context = AppContext()
    return _app_context


def initialize_app_context() -> AppContext:
    """Initialize a fresh application context."""
    global _app_context
    _app_context = AppContext()
    return _app_context


def cleanup_app_context() -> None:
    """Cleanup the global application context."""
    global _app_context
    if _app_context:
        _app_context.cleanup()
        _app_context = None
