import json
from typing import Any, Dict

from src.logmgr import logger
from src.utils.paths import get_config_path


class Config:
    _instance = None
    _config_data: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        config_path = get_config_path()
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._config_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading config from {config_path}", error=e)
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
        return self._config_data


# Global instance
config = Config()
