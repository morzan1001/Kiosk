"""Provides basic logging functionality"""
import logging
from datetime import datetime


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
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if not self.logger.handlers:
            # Stream handler for console output
            stream_handler = logging.StreamHandler()
            stream_formatter = logging.Formatter(self.MESSAGE_PREFIX_FORMAT)
            stream_handler.setFormatter(stream_formatter)
            self.logger.addHandler(stream_handler)  # Log to the screen

        self.update_prefix()  # Make sure the file handler is created/updated

    @staticmethod
    def log_prefix() -> str:
        """Generates and returns log prefix (timestamp) for log file"""
        return f'{datetime.today().year}_{datetime.today().month}'

    def update_prefix(self):
        """Updates the log prefix for log file name to current time"""
        if self.current_prefix != self.log_prefix():
            self.current_prefix = self.log_prefix()

            file_handler = logging.FileHandler(f'kiosk_{self.current_prefix}.log', encoding='utf-8')
            formatter = logging.Formatter(self.MESSAGE_PREFIX_FORMAT)
            file_handler.setFormatter(formatter)

            # Remove existing file handler to prevent duplicate logs
            for handler in self.logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    self.logger.removeHandler(handler)

            self.logger.addHandler(file_handler)

    def format_message(self, msg: str, error=None) -> str:
        """Formats the log message according to whether an error exists"""
        if error:
            return f"{msg} - {error}"
        return msg

    def warning(self, msg: str, error=None):
        """Logs message with level: warning"""
        self.update_prefix()
        self.logger.warning(self.format_message(msg, error))

    def debug(self, msg: str, error=None):
        """Logs message with level: debug"""
        self.update_prefix()
        self.logger.debug(self.format_message(msg, error))

    def info(self, msg: str, error=None):
        """Logs message with level: info"""
        self.update_prefix()
        self.logger.info(self.format_message(msg, error))

    def error(self, msg: str, error=None):
        """Logs message with level: error"""
        self.update_prefix()
        self.logger.error(self.format_message(msg, error))

    def critical(self, msg: str, error=None):
        """Logs message with level: critical"""
        self.update_prefix()
        self.logger.critical(self.format_message(msg, error))

