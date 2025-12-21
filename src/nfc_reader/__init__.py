"""
This package manages the NFC reader operations.
It provides the NFCReader class to interface with the NFC hardware.
"""

# Re-export for convenient imports.
from .nfc_reader import NFCReader  # noqa: F401

__all__ = ["NFCReader"]
