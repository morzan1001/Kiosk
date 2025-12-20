import json
import locale

from src.logmgr import logger
from src.utils.paths import PROJECT_ROOT

TRANSLATIONS = None


def get_system_language():
    """Determine the system language."""
    try:
        system_locale = locale.getlocale()[0]
        if not system_locale:
            # Fallback to getdefaultlocale (deprecated but useful fallback)
            # pylint: disable=deprecated-method
            system_locale = locale.getdefaultlocale()[0]
    except Exception:  # pylint: disable=broad-exception-caught
        system_locale = "en"

    if system_locale and system_locale.startswith("de"):
        return "de"
    return "en"


def load_translation(language_code):
    """Load translation file for the given language code."""
    locale_path = (
        PROJECT_ROOT / "src" / "localization" / "locales" / f"{language_code}.json"
    )
    logger.debug(f"Loading translations from {locale_path}")
    try:
        with open(locale_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as e:
        logger.error(f"Translation file not found: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from translation file: {e}")
        raise


def initialize_translations():
    global TRANSLATIONS
    try:
        language_code = get_system_language()
        logger.debug(f"System language determined: {language_code}")

        TRANSLATIONS = load_translation(language_code)
        logger.debug(f"Translations object initialized: {TRANSLATIONS}")
        logger.info("Translations loaded successfully")
    except Exception as e:
        logger.error(f"Failed to initialize translations: {e}")
        raise


def get_translations() -> dict:
    if TRANSLATIONS is None:
        logger.error("Translations have not been initialized.")
        raise ValueError(
            "Translations have not been initialized. Call initialize_translations() first."
        )
    logger.debug("Translations fetched successfully")
    return TRANSLATIONS
