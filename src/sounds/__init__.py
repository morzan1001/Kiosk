"""
This package manages the audio functionalities of the kiosk system.
It provides the SoundController class to handle sound playback,
and utility functions to initialize and access the sound system.
"""

# Import the SoundController class from the sound_controller module
from .sound_controller import SoundController

# Import the utility functions from the sound_manager module
from .sound_manager import (
    get_sound_controller,
    initialize_sound_controller,
    stop_sound_controller,
)

# Export the SoundController class and utility functions when this package is imported
__all__ = [
    "SoundController",
    "initialize_sound_controller",
    "get_sound_controller",
    "stop_sound_controller",
]
