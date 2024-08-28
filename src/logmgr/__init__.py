"""
This package manages the logging functionality.
It provides the LogMgr class to handle logging operations.
"""

# Import the LogMgr class from the logmgr module
from .logmgr import LogMgr

# Create an instance of LogMgr
logger = LogMgr()

# Export the logger instance when this package is imported
__all__ = ["LogMgr", "logger"]
