import sys
import os
import json
import customtkinter
from customtkinter import CTk
from time import sleep
from src.localization import initialize_translations
from src.localization.translator import get_translations

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.ui.screens.WelcomePage import *
from src.lock import initialize_gpio, cleanup_gpio
from src.logmgr import logger
from src.database.connection import session_manager
from src.email.email_manager import initialize_email_controller, shutdown_scheduler

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "../config.json")
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)

class KioskCTK(CTk):
    def __init__(self, config):
        super().__init__()
        self.translations = get_translations()
        self.admin_password = config["admin"]["password"]
        self.bind("<Escape>", lambda event: self.exit_fullscreen())

    def exit_fullscreen(self):
        logger.debug("Exiting fullscreen mode")
        admin_password = customtkinter.CTkInputDialog(text=self.translations["admin"]["admin_password_prompt"], title=self.translations["admin"]["exit_message"]).get_input()

        if admin_password == self.admin_password:
            self.attributes("-fullscreen", False)
        else:
            from src.ui.components.Message import ShowMessage
            self.message = ShowMessage(self, image="unsuccessful", heading="Error", text=self.translations["general"]["error_message"])
            self.after(5000, self.message.destroy)

def main():
    try:
        logger.debug("Starting application initialization")
        config = load_config()  # Load configuration

        # Initialize translations
        logger.debug("Initializing translations")
        initialize_translations()

        # Initialize database session
        logger.debug("Starting database session")
        session_manager.start_session()
        logger.info("Database session initialized")

        # Initialize GPIO
        logger.debug("Initializing GPIO")
        initialize_gpio(chip=config["gpio"]["chip"], line_number=config["gpio"]["line_number"])
        logger.info("GPIO initialized")

        # Initialize EmailController
        logger.debug("Initializing Email Controller")
        initialize_email_controller(server=config["email"]["smtp_server"], port=config["email"]["smtp_port"], login=config["email"]["login"], password=config["email"]["password"])
        logger.info("Email Controller initialized")

        # Initialize window
        logger.debug("Initializing main window")
        root = KioskCTK(config)

        # Explicitly set fullscreen before everything is set up
        root.after(500, lambda: root.wm_attributes("-fullscreen", True))
        logger.debug("Set application to fullscreen mode")

        set_appearance_mode(config["appearance"]["mode"])  # Use appearance config
        
        logger.debug("Setting up main kiosk frame")
        kiosk_frame = KioskMainFrame(root)
        kiosk_frame.grid(row=0, column=0, sticky="nsew")

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))

        sleep(0.1)
        logger.debug("Starting main application loop")
        root.mainloop()
        
    except Exception as e:
        logger.error("Error initializing application: ", e)
    finally:
        cleanup_gpio()

def on_closing(root):
    logger.info("Exiting application")
    session_manager.close_session()
    shutdown_scheduler()
    cleanup_gpio()
    root.destroy()
    root.quit()

if __name__ == "__main__":
    main()