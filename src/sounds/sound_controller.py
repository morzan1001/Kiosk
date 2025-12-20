import os
import queue
import random
import threading

import sounddevice as sd
import soundfile as sf

from src.logmgr import logger


class SoundController(threading.Thread):
    def __init__(self, pos_dir, neg_dir):
        super().__init__()
        self.pos_dir = pos_dir
        self.neg_dir = neg_dir
        self.queue = queue.Queue()
        self.daemon = True
        self._stop_event = threading.Event()
        logger.debug(
            f"SoundController initialized with directories: Positive: {pos_dir}, Negative: {neg_dir}"
        )

    def run(self):
        while not self._stop_event.is_set():
            try:
                sound_type = self.queue.get(timeout=1)
                self._play_sound(sound_type)
                self.queue.task_done()
            except queue.Empty:
                continue

    def stop(self):
        self._stop_event.set()

    def play_sound(self, sound_type="positive"):
        self.queue.put(sound_type)

    def _play_sound(self, sound_type="positive"):
        logger.debug(f"Preparing to play sound of type: {sound_type}")

        if sound_type == "positive":
            sound_dir = self.pos_dir
        elif sound_type == "negative":
            sound_dir = self.neg_dir
        else:
            logger.error("sound_type must be 'positive' or 'negative'.")
            return

        sound_files = [
            f for f in os.listdir(sound_dir) if f.endswith((".wav", ".mp3", ".ogg"))
        ]
        logger.debug(f"Found {len(sound_files)} sound files in '{sound_dir}'")

        if not sound_files:
            logger.warning("No sound files found in the specified directory.")
            return

        sound_file = random.choice(sound_files)
        sound_path = os.path.join(sound_dir, sound_file)
        logger.debug(f"Selected sound file: {sound_file}")

        try:
            data, fs = sf.read(sound_path)

            # Get the default sample rate without logging warnings
            device_info = sd.query_devices(sd.default.device[1])
            default_fs = int(device_info["default_samplerate"])

            # Only resample if necessary and significantly different
            if abs(fs - default_fs) > 100:
                logger.debug(f"Resampling from {fs}Hz to {default_fs}Hz")
                from scipy import signal

                data = signal.resample(data, int(len(data) * default_fs / fs))
                fs = default_fs
            else:
                fs = default_fs

            sd.play(data, fs)
            sd.wait()
            logger.debug("Sound playback finished")
        except Exception as e:
            logger.error(f"Error playing sound: {str(e)}")

    def find_valid_samplerate(self, desired_samplerate):
        device_info = sd.query_devices(sd.default.device[1])
        supported_samplerates = device_info["default_samplerate"]
        logger.debug(f"Device supports samplerate: {supported_samplerates}")

        if abs(desired_samplerate - supported_samplerates) < 100:
            return int(supported_samplerates)

        logger.warning(
            f"Desired samplerate {desired_samplerate} not supported. Using default {supported_samplerates}"
        )
        return int(supported_samplerates)
