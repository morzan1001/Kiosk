"""
NFC Reader Module.
Provides continuous NFC card reading in a separate thread.
"""

import threading
import time
from typing import Callable, List, Optional

from py532lib.i2c import Pn532_i2c
from py532lib.mifare import Mifare

from src.logmgr import logger

pn532: Pn532_i2c = Pn532_i2c()
pn532.SAMconfigure()
mifare: Mifare = Mifare()


class NFCReader:
    """
    NFC Reader class that continuously reads NFC cards in a separate thread.

    Attributes:
        thread: The background thread for reading NFC data.
    """

    def __init__(self) -> None:
        """
        Initialize the NFCReader class.
        Starts a separate thread for continuous reading of NFC data.
        """
        self._lock: threading.Lock = threading.Lock()
        self._stop_event: threading.Event = threading.Event()
        self._latest_nfcid: Optional[List[int]] = None
        self._callbacks: List[Callable[[str], None]] = []
        self.thread: threading.Thread = threading.Thread(target=self._read_nfc)
        self.thread.start()

    def _read_nfc(self) -> None:
        """
        Internal method executed in a separate thread.
        Continuously reads NFC data and updates _latest_nfcid.
        """
        while not self._stop_event.is_set():
            try:
                uid = mifare.scan_field()
                if uid:
                    f_uid: List[int] = [int(byte) for byte in uid]
                    with self._lock:
                        self._latest_nfcid = f_uid
                    # Notify all registered callbacks outside the lock
                    self._notify_callbacks()
                    # Prevent multiple reads of the same card immediately and reduce CPU load
                    time.sleep(0.5)
                else:
                    # Small sleep to prevent CPU hogging when no card is present
                    time.sleep(0.1)
            except Exception:  # pylint: disable=broad-exception-caught
                # NFC hardware/driver stack can raise a wide range of errors.
                # We keep the reader thread alive and log full context.
                logger.exception("Error reading NFC data")
                time.sleep(1)

    def get_nfcid(self) -> Optional[List[int]]:
        """
        Returns the latest read NFC ID.
        Uses a lock for thread safety.

        Returns:
            List of bytes representing the NFC ID, or None.
        """
        with self._lock:
            return self._latest_nfcid

    def get_nfcid_str(self) -> Optional[str]:
        """
        Returns the latest read NFC ID as a string.
        Uses a lock for thread safety.

        Returns:
            Hex string representation of the NFC ID, or None.
        """
        with self._lock:
            if self._latest_nfcid is not None:
                nfcid_str: str = "".join(format(byte, "02x") for byte in self._latest_nfcid)
                return nfcid_str
            return None

    def stop(self, timeout: float | None = None) -> None:
        """Stop the reader thread.

        Args:
            timeout: Optional timeout (seconds) for waiting on the thread.
                If None, wait indefinitely.
        """
        self._stop_event.set()
        if threading.current_thread() == self.thread:
            return

        try:
            self.thread.join(timeout=timeout)
        except RuntimeError:
            logger.exception("Failed to join NFC reader thread")
            return

        if timeout is not None and self.thread.is_alive():
            logger.warning("NFC reader thread did not stop within %.2fs", timeout)

    def register_callback(self, callback: Callable[[str], None]) -> None:
        """
        Register a callback function to be called when a new NFC ID is read.

        Args:
            callback: Function that takes the NFC ID string as argument.
        """
        with self._lock:
            self._callbacks.append(callback)

    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks with the latest NFC ID."""
        nfcid_str: Optional[str] = self.get_nfcid_str()
        if nfcid_str:
            # Create a copy of callbacks to avoid holding the lock during callback execution.
            callbacks: List[Callable[[str], None]]
            with self._lock:
                callbacks = list(self._callbacks)

            for callback in callbacks:
                callback(nfcid_str)
        else:
            logger.debug("No NFC ID to notify callbacks")
