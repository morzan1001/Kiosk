"""
This package manages the NFC reader operations.
It provides the NFC_READER class to interface with the NFC hardware.
"""

# Import the NFC_READER class from the nfc_reader module
from .nfc_reader import NFCReader

# Export the NFC_READER class when this package is imported
__all__ = ["NFC_READER"]
