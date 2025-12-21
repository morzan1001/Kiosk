"""
Main module for the Kiosk application.
Initializes the application, database, and UI.
"""

import os
import sys
from time import sleep
from typing import Optional

import customtkinter
from customtkinter import CTk, set_appearance_mode

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# pylint: disable=wrong-import-position
from src.app_context import cleanup_app_context, initialize_app_context  # noqa: E402
from src.database.connection import initialize_database  # noqa: E402
from src.database.connection import session_manager
from src.localization import initialize_translations  # noqa: E402
from src.localization.translator import get_translations  # noqa: E402
from src.lock import cleanup_gpio, initialize_gpio  # noqa: E402
from src.logmgr import logger  # noqa: E402
from src.messaging.email import initialize_email_controller  # noqa: E402
from src.messaging.email.email_manager import shutdown_scheduler  # noqa: E402
from src.messaging.mattermost import initialize_mattermost_controller  # noqa: E402
from src.sounds.sound_manager import (  # noqa: E402
    initialize_sound_controller,
    stop_sound_controller,
)
from src.ui.components.Message import ShowMessage  # noqa: E402
from src.ui.screens.welcome_page import KioskMainFrame  # noqa: E402
from src.utils.config import config  # noqa: E402
from src.utils.paths import PROJECT_ROOT  # noqa: E402


def validate_database_config() -> None:
    """Validate database configuration."""
    db_type: str = config.get("database.type", "").lower()

    if not db_type:
        raise ValueError("Database type not specified in configuration")

    if db_type == "sqlite":
        if not config.get("database.sqlite.path"):
            logger.warning("SQLite database path not specified, using default")

    elif db_type == "postgresql":
        pg_config: dict = config.get("database.postgresql", {})
        required_fields: list[str] = ["host", "database", "username", "password"]

        for field in required_fields:
            if not pg_config.get(field):
                raise ValueError(f"PostgreSQL {field} not specified in configuration")

    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    logger.info("Database configuration validated for %s", db_type.upper())


class KioskCTK(CTk):
    """Main Kiosk Application Class inheriting from CTk."""

    def __init__(self) -> None:
        super().__init__()
        self.translations: dict = get_translations()
        self.admin_password: Optional[str] = config.get("admin.password")
        self.message: Optional[object] = None
        self.bind("<Escape>", lambda event: self.exit_fullscreen())

    def exit_fullscreen(self) -> None:
        """Exit fullscreen mode if admin password is correct."""
        logger.debug("Exiting fullscreen mode")
        admin_password: Optional[str] = customtkinter.CTkInputDialog(
            text=self.translations["admin"]["admin_password_prompt"],
            title=self.translations["admin"]["exit_message"],
        ).get_input()

        if admin_password == self.admin_password:
            self.attributes("-fullscreen", False)
        else:
            self.message = ShowMessage(
                self,
                image="unsuccessful",
                heading=self.translations["general"]["error_heading"],
                text=self.translations["general"]["error_message"],
            )
            self.after(5000, self.message.destroy)


def main() -> None:
    """Main entry point for the application."""
    # Initialize the application context
    initialize_app_context()

    try:
        logger.debug("Starting application initialization")

        logger.debug("Validating database configuration")
        validate_database_config()

        logger.debug("Initializing database connection")
        initialize_database(config.get_all())
        logger.info("Database connection initialized")

        logger.debug("Initializing translations")
        initialize_translations()

        logger.debug("Starting database session")
        session_manager.start_session()
        logger.info("Database session initialized")

        logger.debug("Initializing GPIO")
        initialize_gpio(chip=config.get("gpio.chip"), line_number=config.get("gpio.line_number"))
        logger.info("GPIO initialized")

        logger.debug("Initializing Email Controller")
        initialize_email_controller(
            server=config.get("email.smtp_server"),
            port=config.get("email.smtp_port"),
            login=config.get("email.login"),
            password=config.get("email.password"),
        )
        logger.info("Email Controller initialized")

        if config.get("mattermost.enabled"):
            logger.debug("Initializing Mattermost Controller")
            initialize_mattermost_controller(
                base_url=config.get("mattermost.base_url"),
                bot_token=config.get("mattermost.bot_token"),
            )
            logger.info("Mattermost Controller initialized")
        else:
            logger.info("Mattermost notifications are disabled in configuration")

        if config.get("sound.enabled"):
            logger.debug("Initializing Sound Controller")
            pos_sound_dir = config.get("sound.positive_directory")
            neg_sound_dir = config.get("sound.negative_directory")
            initialize_sound_controller(pos_sound_dir, neg_sound_dir)
        else:
            logger.info("Sound is disabled in configuration")

        logger.debug("Initializing main window")

        try:
            customtkinter.set_default_color_theme(
                str(PROJECT_ROOT / "src" / "ui" / "kiosk_theme.json")
            )
            logger.info("Loaded custom kiosk theme")
        except (OSError, ValueError) as e:
            logger.warning("Could not load custom theme, using default: %s", e)
            customtkinter.set_default_color_theme("green")

        root = KioskCTK()

        # Explicitly set fullscreen before everything is set up
        root.after(500, lambda: root.wm_attributes("-fullscreen", True))
        logger.debug("Set application to fullscreen mode")

        set_appearance_mode(config.get("appearance.mode", "light"))

        logger.debug("Setting up main kiosk frame")
        kiosk_frame = KioskMainFrame(root)
        kiosk_frame.grid(row=0, column=0, sticky="nsew")

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

        sleep(0.1)
        logger.debug("Starting main application loop")
        root.mainloop()

    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Error initializing application")
    finally:
        cleanup_app_context()
        cleanup_gpio()


def on_closing(root: CTk) -> None:
    """Handle application closing event."""
    logger.info("Exiting application")
    shutdown_scheduler()
    session_manager.close_session()
    stop_sound_controller()
    cleanup_app_context()
    cleanup_gpio()
    root.destroy()
    root.quit()


if __name__ == "__main__":
    main()
