from logmgr import logger
from src.sounds.sound_controller import SoundController

sound_controller = None

def initialize_sound_controller(pos_dir: str, neg_dir: str):
    global sound_controller
    sound_controller = SoundController(pos_dir, neg_dir)
    logger.debug(f"SoundController initialized with directories: Positive: {pos_dir}, Negative: {neg_dir}")