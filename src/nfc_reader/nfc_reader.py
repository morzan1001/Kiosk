import threading
import time

from py532lib.i2c import Pn532_i2c
from py532lib.mifare import Mifare

from src.logmgr import logger

pn532 = Pn532_i2c()
pn532.SAMconfigure()
mifare = Mifare()


class NFCReader:
    """
    Initializes the NFC_READER class.
    Starts a separate thread for continuous reading of NFC data.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._latest_nfcid = None
        self._callbacks = []
        self.thread = threading.Thread(target=self._read_nfc)
        self.thread.start()

    def _read_nfc(self):
        """
        Internal method executed in a separate thread.
        Continuously reads NFC data and updates _latest_nfcid.
        """
        while not self._stop_event.is_set():
            try:
                uid = mifare.scan_field()
                if uid:
                    f_uid = [int(byte) for byte in uid]
                    with self._lock:
                        self._latest_nfcid = f_uid
                    # Notify all registered callbacks outside the lock
                    self._notify_callbacks()
                    # Prevent multiple reads of the same card immediately and reduce CPU load
                    time.sleep(0.5)
                else:
                    # Small sleep to prevent CPU hogging when no card is present
                    time.sleep(0.1)
            except Exception as e:
                logger.error("Error reading NFC data: " + str(e))
                time.sleep(1)

    def get_nfcid(self):
        """
        Returns the latest read NFC ID.
        Uses a lock for thread safety.
        """
        with self._lock:
            return self._latest_nfcid

    def get_nfcid_str(self):
        """
        Returns the latest read NFC ID as a string.
        Uses a lock for thread safety.
        """
        with self._lock:
            if self._latest_nfcid is not None:
                nfcid_str = "".join(format(byte, "02x") for byte in self._latest_nfcid)
                return nfcid_str
            return None

    def stop(self):
        """
        Stops the reading thread and waits for it to fully halt.
        """
        self._stop_event.set()
        if threading.current_thread() != self.thread:
            self.thread.join()

    def register_callback(self, callback):
        """Register a callback function to be called when a new NFC ID is read."""
        with self._lock:
            self._callbacks.append(callback)

    def _notify_callbacks(self):
        """Notify all registered callbacks with the latest NFC ID."""
        nfcid_str = self.get_nfcid_str()
        if nfcid_str:
            # Create a copy of the callbacks list to avoid holding the lock during callback execution
            callbacks = None
            with self._lock:
                callbacks = list(self._callbacks)

            for callback in callbacks:
                callback(nfcid_str)
        else:
            logger.debug("No NFC ID to notify callbacks")
