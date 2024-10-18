import os
import random
import pygame
from src.logmgr import logger

class SoundController:
    def __init__(self, pos_dir, neg_dir):
        """
        Initialize the SoundController with directories for positive and negative sounds.
        """
        logger.debug("Initializing SoundController")
        
        self.pos_dir = pos_dir
        self.neg_dir = neg_dir
        logger.debug(f"Positive sound directory set to: {pos_dir}")
        logger.debug(f"Negative sound directory set to: {neg_dir}")

        pygame.mixer.init()  # Initialize the mixer module
        logger.debug("Pygame mixer initialized")

    def play_sound(self, sound_type='positive'):
        """
        Play a random sound from the specified folder: "positive" or "negative".
        """
        logger.debug(f"Preparing to play sound of type: {sound_type}")

        if sound_type == 'positive':
            sound_dir = self.pos_dir
        elif sound_type == 'negative':
            sound_dir = self.neg_dir
        else:
            logger.error("sound_type must be 'positive' or 'negative'.")
            raise ValueError("sound_type must be 'positive' or 'negative'.")

        # Get a list of all mp3 files in the directory
        sound_files = [f for f in os.listdir(sound_dir) if f.endswith('.mp3')]
        logger.debug(f"Found {len(sound_files)} sound files in '{sound_dir}'")

        if not sound_files:
            logger.warning("No sound files found in the specified directory.")
            return
        
        # Choose a random sound file
        sound_file = random.choice(sound_files)
        sound_path = os.path.join(sound_dir, sound_file)
        logger.debug(f"Selected sound file: {sound_file}")

        # Play the selected sound
        logger.info(f"Playing sound file: {sound_file}")
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()

        # Waiting for the sound to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        logger.debug("Sound playback finished")