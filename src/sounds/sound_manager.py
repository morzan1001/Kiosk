from logmgr import logger
from src.sounds.sound_controller import SoundController

sound_controller = None

def initialize_sound_controller(pos_dir: str, neg_dir: str):
    global sound_controller
    sound_controller = SoundController(pos_dir, neg_dir)
    sound_controller.start()  # Start the thread
    logger.debug(f"SoundController thread started")

def get_sound_controller():
    global sound_controller
    if sound_controller is None:
        logger.error("SoundController is not initialized")
    return sound_controller

def stop_sound_controller():
    global sound_controller
    if sound_controller:
        sound_controller.stop()
        sound_controller.join()
        sound_controller = None
        logger.debug("SoundController stopped and thread joined")