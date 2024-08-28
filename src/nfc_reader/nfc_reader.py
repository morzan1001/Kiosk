import threading
from logmgr import logger
from py532lib.i2c import Pn532_i2c
from py532lib.mifare import Mifare

pn532 = Pn532_i2c()
pn532.SAMconfigure()
mifare = Mifare()

class NFC_READER:
    """
    Initializes the NFC_READER class.
    Starts a separate thread for continuous reading of NFC data.
    """

    def __init__(self):
        self._lock = threading.Lock()  # Lock for thread-safe access to _latest_nfcid
        self._stop_event = threading.Event()  # Event to stop the reading thread
        self._latest_nfcid = None  # Variable to store the latest read NFC ID
        self._callbacks = []  # List of callback functions to be called when a new NFC ID is read
        self.thread = threading.Thread(target=self._read_nfc)  # Initializing the reading thread
        self.thread.start()  # Starting the reading thread

    def _read_nfc(self):
        """
        Internal method executed in a separate thread.
        Continuously reads NFC data and updates _latest_nfcid.
        """
        while not self._stop_event.is_set():
            try:
                # Use the scan_field method to get the UID
                uid = mifare.scan_field()
                if uid:
                    # Convert UID to list of integers
                    F_UID = [int(byte) for byte in uid]
                    # Update _latest_nfcid in a thread-safe manner
                    with self._lock:
                        self._latest_nfcid = F_UID
                    # Notify all registered callbacks outside the lock
                    self._notify_callbacks()
                else:
                    logger.debug("No NFC data found")
            except Exception as e:
                logger.error("Error reading NFC data: " + str(e))

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
                callbacks = list(self._callbacks)  # Copy the callbacks to avoid holding the lock
            
            for callback in callbacks:
                callback(nfcid_str)
        else:
            logger.debug("No NFC ID to notify callbacks")