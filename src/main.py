import sys
import os
import customtkinter
from customtkinter import CTk
from time import sleep
from src.localization import initialize_translations
from src.localization.translator import get_translations
from src.sounds.sound_manager import initialize_sound_controller

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.ui.screens.WelcomePage import *
from src.lock import initialize_gpio, cleanup_gpio
from src.logmgr import logger
from src.database.connection import session_manager

class KioskCTK(CTk):
    def __init__(self):
        super().__init__()
        self.translations = get_translations()  # Get translations after they have been initialized
        self.bind("<Escape>", lambda event: self.exit_fullscreen())

    def exit_fullscreen(self):
        logger.debug("Exiting fullscreen mode")
        admin_password = customtkinter.CTkInputDialog(text=self.translations["admin"]["admin_password_prompt"], title=self.translations["admin"]["exit_message"]).get_input()

        if admin_password == "admin123":
            self.attributes("-fullscreen", False)
        else:
            from src.ui.components.Message import ShowMessage
            self.message = ShowMessage(self, image="unsuccessful", heading="Error", text=self.translations["general"]["error_message"])  
            self.after(5000, self.message.destroy)

def main():
    try:
        logger.debug("Starting application initialization")
        # Initialize translations
        logger.debug("Initializing translations")
        initialize_translations()

        # Initialize database session
        logger.debug("Starting database session")
        session_manager.start_session()
        logger.info("Database session initialized")


        # Initialize GPIO
        logger.debug("Initializing GPIO")
        initialize_gpio(chip="/dev/gpiochip0", line_number=4)
        logger.info("GPIO initialized")

        # Initialize SoundController
        logger.debug("Initializing Sound Controller")
        pos_sound_dir = "sounds/positive/"  
        neg_sound_dir = "sounds/negative/" 
        initialize_sound_controller(pos_sound_dir, neg_sound_dir)

        # Initialize window
        logger.debug("Initializing main window")
        root = KioskCTK()

        # Explicitly set fullscreen before everything is set up
        root.after(500, lambda: root.wm_attributes("-fullscreen", True))
        logger.debug("Set application to fullscreen mode")

        set_appearance_mode("Dark")
       
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
    session_manager.close_session()  # Close the database session
    cleanup_gpio()
    root.destroy()
    root.quit()

if __name__ == "__main__":
    main()