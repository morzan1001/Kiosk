from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
IMAGES_DIR = SRC_DIR / "images"
CONFIG_FILE = PROJECT_ROOT / "config.json"


def get_image_path(filename: str) -> str:
    """Returns the absolute path to an image file."""
    return str(IMAGES_DIR / filename)


def get_config_path() -> str:
    """Returns the absolute path to the config file."""
    return str(CONFIG_FILE)


def get_template_dir() -> str:
    """Returns the absolute path to the email templates directory."""
    return str(SRC_DIR / "messaging" / "email" / "templates")
