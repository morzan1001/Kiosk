"""
This package manages the audio functionalities of the kiosk system.
It provides the SoundController class to handle sound playback,
and a utility function to initialize the sound system.
"""

# Import the SoundController class from the sound_controller module
from .sound_controller import SoundController

# Import the utility function from the sound_manager module
from .sound_manager import SOUND_CONTROLLER, initialize_sound_controller

# Export the SoundController class and utility function when this package is imported
__all__ = ["SoundController", "initialize_sound_controller", "SOUND_CONTROLLER"]
