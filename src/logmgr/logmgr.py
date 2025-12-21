"""Logging utilities.

This project historically used a small wrapper (`LogMgr`) around Python's
`logging` module to simplify usage and automatically rotate log files monthly.

The wrapper is kept for backwards compatibility, but its public methods now
accept the standard logging API shape (`msg, *args, **kwargs`) so call sites can
use lazy formatting (e.g. ``logger.info("Value: %s", value)``) and
``logger.exception(...)``.
"""

import json
import logging
from datetime import datetime

from src.utils.paths import get_config_path


class LogMgr:
    """
    Helper class for basic logging functionality provided by python
    """

    LOGGING_PATH = ""
    MESSAGE_PREFIX_FORMAT = "%(asctime)s\t[%(levelname)s] : %(message)s"

    current_prefix = ""
    logger = None

    def __init__(self):
        """Class constructor"""
        self.logger = logging.getLogger("Kiosk")
        self.logger.propagate = False

        # Setup basic stream handler first so we can log errors during config loading
        if not self.logger.handlers:
            stream_handler = logging.StreamHandler()
            stream_formatter = logging.Formatter(self.MESSAGE_PREFIX_FORMAT)
            stream_handler.setFormatter(stream_formatter)
            self.logger.addHandler(stream_handler)

        # Default to INFO if no config present
        log_level = "INFO"
        self.logger.setLevel(logging.INFO)

        try:
            config_path = get_config_path()
            with open(config_path, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
                log_level = config.get("logging", {}).get("level", "INFO")
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            self.logger.warning("Could not load logging config, defaulting to INFO: %s", e)

        self.logger.setLevel(getattr(logging, log_level))

        self.update_prefix()  # Make sure the file handler is created/updated

    @staticmethod
    def log_prefix() -> str:
        """Generates and returns log prefix (timestamp) for log file"""
        return f"{datetime.today().year}_{datetime.today().month}"

    def update_prefix(self):
        """Updates the log prefix for log file name to current time"""
        if self.current_prefix != self.log_prefix():
            self.current_prefix = self.log_prefix()

            file_handler = logging.FileHandler(f"kiosk_{self.current_prefix}.log", encoding="utf-8")
            formatter = logging.Formatter(self.MESSAGE_PREFIX_FORMAT)
            file_handler.setFormatter(formatter)

            # Remove existing file handler to prevent duplicate logs
            for handler in self.logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    self.logger.removeHandler(handler)

            self.logger.addHandler(file_handler)

    def format_message(self, msg: str, error=None) -> str:
        """Formats a message by optionally appending an error string."""
        if error is None:
            return msg
        return f"{msg} - {error}"

    def _log(self, level_method, msg: str, *args, error=None, **kwargs):
        """Internal helper that mimics the stdlib logging API.

        Supports the project's legacy `error=` keyword / second positional arg
        while allowing lazy formatting via `*args`.
        """
        # Backwards compatibility:
        # Historically the wrapper used a second positional arg as `error`.
        # With stdlib-like logging (`msg, *args`) that would otherwise be treated
        # as formatting args and can raise at runtime if `msg` has no placeholders.
        if error is None and len(args) == 1 and "%" not in msg:
            error = args[0]
            args = ()

        self.update_prefix()
        msg = self.format_message(msg, error)
        level_method(msg, *args, **kwargs)

    def warning(self, msg: str, *args, error=None, **kwargs):
        """Logs message with level: warning."""
        self._log(self.logger.warning, msg, *args, error=error, **kwargs)

    def debug(self, msg: str, *args, error=None, **kwargs):
        """Logs message with level: debug."""
        self._log(self.logger.debug, msg, *args, error=error, **kwargs)

    def info(self, msg: str, *args, error=None, **kwargs):
        """Logs message with level: info."""
        self._log(self.logger.info, msg, *args, error=error, **kwargs)

    def error(self, msg: str, *args, error=None, **kwargs):
        """Logs message with level: error."""
        self._log(self.logger.error, msg, *args, error=error, **kwargs)

    def critical(self, msg: str, *args, error=None, **kwargs):
        """Logs message with level: critical."""
        self._log(self.logger.critical, msg, *args, error=error, **kwargs)

    def exception(self, msg: str, *args, error=None, **kwargs):
        """Log a message with level ERROR and exception information."""
        self._log(self.logger.exception, msg, *args, error=error, **kwargs)
