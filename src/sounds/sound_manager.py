from src.logmgr import logger
from src.sounds.sound_controller import SoundController

SOUND_CONTROLLER = None


def initialize_sound_controller(pos_dir: str, neg_dir: str):
    global SOUND_CONTROLLER
    SOUND_CONTROLLER = SoundController(pos_dir, neg_dir)
    SOUND_CONTROLLER.start()
    logger.debug("SoundController thread started")


def get_sound_controller():
    if SOUND_CONTROLLER is None:
        logger.error("SoundController is not initialized")
    return SOUND_CONTROLLER


def stop_sound_controller():
    global SOUND_CONTROLLER
    if SOUND_CONTROLLER:
        SOUND_CONTROLLER.stop()
        SOUND_CONTROLLER.join()
        SOUND_CONTROLLER = None
        logger.debug("SoundController stopped and thread joined")
