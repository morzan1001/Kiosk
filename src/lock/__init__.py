"""
This package manages the locking mechanisms using GPIO controllers.
It provides the GPIOController class to interface with the hardware,
and utility functions to initialize and clean up the GPIO resources.
"""

# Import the GPIOController class from the lock module
from .lock import GPIOController

# Import the utility functions from the gpio_manager module
from .gpio_manager import initialize_gpio, cleanup_gpio

# Export the GPIOController class and utility functions when this package is imported
__all__ = ["GPIOController", "initialize_gpio", "cleanup_gpio"]