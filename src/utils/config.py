"""Configuration loader.

Loads `config.json` once (singleton-style) and provides dot-notation access via
`Config.get`.
"""

import json
import threading
from typing import Any, Dict

from src.logmgr import logger
from src.utils.paths import get_config_path


class Config:
    """Singleton configuration accessor for `config.json`."""

    _instance = None
    _lock = threading.Lock()
    _config_data: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super(Config, cls).__new__(cls)
                    cls._instance = instance
                    instance._load()
        return cls._instance

    def _load(self):
        """Load configuration JSON from disk.

        On failure, an empty config is used.
        """
        config_path = get_config_path()
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._config_data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Error loading config from %s", config_path, error=e)
            # Fallback or re-raise depending on severity
            self._config_data = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key (dot notation supported for nested keys)."""
        keys = key.split(".")
        value = self._config_data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_all(self) -> Dict[str, Any]:
        """Return the full configuration dict."""
        return self._config_data


# Global instance
config = Config()
