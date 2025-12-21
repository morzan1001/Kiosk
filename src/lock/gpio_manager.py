"""
GPIO Manager Module.
Provides initialization and access functions for the GPIOController.
"""

from typing import Optional

from src.app_context import get_app_context
from src.lock.lock import GPIOController
from src.logmgr import logger


def initialize_gpio(chip: str = "/dev/gpiochip0", line_number: int = 4) -> None:
    """
    Initialize the GPIO controller.

    Args:
        chip: GPIO chip device path.
        line_number: GPIO line number to control.

    Raises:
        Exception: If GPIO initialization fails.
    """
    ctx = get_app_context()
    try:
        logger.debug("Initializing GPIOController with chip %s and line %s", chip, line_number)
        ctx.gpio_controller = GPIOController(chip, line_number)
        logger.info("GPIO started successfully")
        ctx.gpio_controller.deactivate()  # Close Lock by default
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Error starting GPIO")
        raise


def get_gpio_controller() -> Optional[GPIOController]:
    """
    Get the initialized GPIOController instance.

    Returns:
        The GPIOController instance or None if not initialized.
    """
    ctx = get_app_context()
    if ctx.gpio_controller is None:
        logger.error("GPIO Controller is not initialized")
    return ctx.gpio_controller


def cleanup_gpio() -> None:
    """Cleanup and release GPIO resources."""
    ctx = get_app_context()
    if ctx.gpio_controller:
        try:
            ctx.gpio_controller.cleanup()
            ctx.gpio_controller = None
            logger.info("GPIO cleanup done")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Error during GPIO cleanup")
