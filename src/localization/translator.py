"""Translation loading and access helpers.

This module loads the locale-specific JSON file into a global cache via
initialize_translations() and exposes it via get_translations().
"""

import json
import locale
from dataclasses import dataclass
from typing import Optional

from src.logmgr import logger
from src.utils.paths import PROJECT_ROOT


@dataclass
class _TranslationState:
    translations: Optional[dict] = None


_STATE = _TranslationState()


def get_system_language():
    """Determine the system language."""
    try:
        system_locale = locale.getlocale()[0]
        if system_locale is None:
            # Ensure a locale is set, then re-read.
            locale.setlocale(locale.LC_ALL, "")
            system_locale = locale.getlocale()[0]
        if system_locale is None:
            return "en"
    except (ValueError, locale.Error):
        return "en"

    return "de" if system_locale.startswith("de") else "en"


def load_translation(language_code):
    """Load translation file for the given language code."""
    locale_path = PROJECT_ROOT / "src" / "localization" / "locales" / f"{language_code}.json"
    logger.debug("Loading translations from %s", locale_path)
    try:
        with open(locale_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as e:
        logger.error("Translation file not found: %s", e)
        raise
    except json.JSONDecodeError as e:
        logger.error("Error decoding JSON from translation file: %s", e)
        raise


def initialize_translations():
    """Initialize the global translations cache based on the system language."""
    try:
        language_code = get_system_language()
        logger.debug("System language determined: %s", language_code)

        _STATE.translations = load_translation(language_code)
        logger.debug("Translations object initialized")
        logger.info("Translations loaded successfully")
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to initialize translations", error=e)
        raise


def get_translations() -> dict:
    """Return the global translations dict (must be initialized first)."""
    if _STATE.translations is None:
        logger.error("Translations have not been initialized.")
        raise ValueError(
            "Translations have not been initialized. Call initialize_translations() first."
        )
    logger.debug("Translations fetched successfully")
    return _STATE.translations
