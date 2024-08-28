import os
import json
import locale

from logmgr import logger

translations = None  # Initialize translations variable

def get_system_language():
    # Get the system's language setting
    system_locale = locale.getdefaultlocale()[0]
    if system_locale.startswith('de'):
        return 'de'
    else:
        return 'en'

def load_translation(language_code):
    # Path to the locale files
    locale_path = os.path.join(os.path.dirname(__file__), "locales", f"{language_code}.json")
    logger.debug(f"Loading translations from {locale_path}")
    try:
        with open(locale_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError as e:
        logger.error(f"Translation file not found: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from translation file: {e}")
        raise

def initialize_translations():
    global translations  # Use the global translations variable
    try:
        # Determine system language
        language_code = get_system_language()
        logger.debug(f"System language determined: {language_code}")

        # Load translations
        translations = load_translation(language_code)
        logger.debug(f"Translations object initialized: {translations}")
        logger.info("Translations loaded successfully")
    except Exception as e:
        logger.error(f"Failed to initialize translations: {e}")
        raise

def get_translations():
    global translations  # Use the global translations variable
    if translations is None:
        logger.error("Translations have not been initialized.")
        raise ValueError("Translations have not been initialized. Call initialize_translations() first.")
    logger.debug("Translations fetched successfully")
    return translations