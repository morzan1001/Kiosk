"""
Sound Manager Module.
Provides initialization and access functions for the SoundController.
"""

from typing import Optional

from src.app_context import get_app_context
from src.logmgr import logger
from src.sounds.sound_controller import SoundController


def initialize_sound_controller(pos_dir: str, neg_dir: str) -> None:
    """
    Initialize the sound controller and start the thread.

    Args:
        pos_dir: Path to directory with positive sound files.
        neg_dir: Path to directory with negative sound files.
    """
    ctx = get_app_context()
    ctx.sound_controller = SoundController(pos_dir, neg_dir)
    ctx.sound_controller.start()
    logger.debug("SoundController thread started")


def get_sound_controller() -> Optional[SoundController]:
    """
    Get the initialized SoundController instance.

    Returns:
        The SoundController instance or None if not initialized.
    """
    ctx = get_app_context()
    if ctx.sound_controller is None:
        logger.error("SoundController is not initialized")
    return ctx.sound_controller


def stop_sound_controller() -> None:
    """Stop and cleanup the sound controller."""
    ctx = get_app_context()
    if ctx.sound_controller:
        ctx.sound_controller.stop()
        ctx.sound_controller.join()
        ctx.sound_controller = None
        logger.debug("SoundController stopped and thread joined")
