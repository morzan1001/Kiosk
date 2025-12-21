"""
Sound Controller Module.
Manages audio playback for positive and negative feedback sounds.
"""

import os
import queue
import secrets
import threading
from typing import List, Literal, Optional

import numpy as np
import sounddevice as sd
import soundfile as sf
from numpy.typing import NDArray
from scipy import signal

from src.logmgr import logger

SoundType = Literal["positive", "negative"]


class SoundController(threading.Thread):
    """
    Thread-based sound controller for playing feedback sounds.

    Attributes:
        pos_dir: Directory path containing positive feedback sound files.
        neg_dir: Directory path containing negative feedback sound files.
    """

    def __init__(self, pos_dir: str, neg_dir: str) -> None:
        """
        Initialize the SoundController.

        Args:
            pos_dir: Path to directory with positive sound files.
            neg_dir: Path to directory with negative sound files.
        """
        super().__init__()
        self.pos_dir: str = pos_dir
        self.neg_dir: str = neg_dir
        self.queue: queue.Queue[SoundType] = queue.Queue()
        self.daemon: bool = True
        self._stop_event: threading.Event = threading.Event()
        logger.debug(
            (
                f"SoundController initialized with directories: Positive: {pos_dir}, "
                f"Negative: {neg_dir}"
            )
        )

    def run(self) -> None:
        """Main thread loop that processes the sound queue."""
        while not self._stop_event.is_set():
            try:
                sound_type: SoundType = self.queue.get(timeout=1)
                self._play_sound(sound_type)
                self.queue.task_done()
            except queue.Empty:
                continue

    def stop(self) -> None:
        """Signal the thread to stop."""
        self._stop_event.set()

    def play_sound(self, sound_type: SoundType = "positive") -> None:
        """
        Queue a sound to be played.

        Args:
            sound_type: Type of sound to play ('positive' or 'negative').
        """
        self.queue.put(sound_type)

    def _get_sound_files(self, sound_dir: str) -> List[str]:
        """
        Get list of sound files from a directory.

        Args:
            sound_dir: Directory to search for sound files.

        Returns:
            List of filenames ending in .wav, .mp3, or .ogg.
        """
        return [f for f in os.listdir(sound_dir) if f.endswith((".wav", ".mp3", ".ogg"))]

    def _find_output_device(self) -> Optional[int]:
        """
        Find an available audio output device.

        Returns:
            Device index or None if no device available.
        """
        output_device: Optional[int] = sd.default.device[1]
        if output_device is None or output_device < 0:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if dev["max_output_channels"] > 0:
                    logger.debug("Using audio device: %s (index %s)", dev["name"], i)
                    return i
            return None
        return output_device

    def _resample_audio(
        self, data: NDArray[np.float64], original_fs: int, target_fs: int
    ) -> NDArray[np.float64]:
        """
        Resample audio data to a target sample rate.

        Args:
            data: Audio data array.
            original_fs: Original sample rate.
            target_fs: Target sample rate.

        Returns:
            Resampled audio data.
        """
        logger.debug("Resampling from %sHz to %sHz", original_fs, target_fs)
        new_length: int = int(len(data) * target_fs / original_fs)
        return signal.resample(data, new_length)

    def _play_sound(self, sound_type: SoundType = "positive") -> None:
        """
        Internal method to play a sound.

        Args:
            sound_type: Type of sound to play.
        """
        logger.debug("Preparing to play sound of type: %s", sound_type)

        if sound_type == "positive":
            sound_dir: str = self.pos_dir
        elif sound_type == "negative":
            sound_dir = self.neg_dir
        else:
            logger.error("sound_type must be 'positive' or 'negative'.")
            return

        sound_files: List[str] = self._get_sound_files(sound_dir)
        logger.debug("Found %s sound files in '%s'", len(sound_files), sound_dir)

        if not sound_files:
            logger.warning("No sound files found in the specified directory.")
            return

        sound_file: str = secrets.choice(sound_files)
        sound_path: str = os.path.join(sound_dir, sound_file)
        logger.debug("Selected sound file: %s", sound_file)

        try:
            output_device: Optional[int] = self._find_output_device()
            if output_device is None:
                logger.warning("No audio output device available, skipping sound playback")
                return

            data: NDArray[np.float64]
            fs: int
            data, fs = sf.read(sound_path)

            device_info = sd.query_devices(output_device)
            default_fs: int = int(device_info["default_samplerate"])

            if abs(fs - default_fs) > 100:
                data = self._resample_audio(data, fs, default_fs)
                fs = default_fs
            else:
                fs = default_fs

            sd.play(data, fs, device=output_device)
            sd.wait()
            logger.debug("Sound playback finished")
        except (IOError, ValueError, RuntimeError, sd.PortAudioError) as e:
            logger.error("Error playing sound: %s", e)
