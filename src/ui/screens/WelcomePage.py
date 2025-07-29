from typing import List
from customtkinter import CTkFrame, CTkLabel, CTkImage
from src.localization.translator import get_translations
from src.ui.components.Message import ShowMessage
from PIL import Image
from src.ui.screens.AdminMain import AdminMainFrame
from src.ui.screens.UserMain import UserMainPage
from src.database import get_db, User, Item
from src.lock.gpio_manager import get_gpio_controller
from src.nfc_reader import NFCReader
from src.logmgr import logger
from src.sounds.sound_manager import sound_controller

class KioskMainFrame(CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.translations = get_translations()
        self.nfc_reader = NFCReader()
        self.session = get_db()
        self.gpio_controller= get_gpio_controller()

        self.parent = parent
        self.parent.title(self.translations["general"]["kiosk_title"])
        self.parent.geometry("800x480")
        self.configure(fg_color="transparent")

        # Configure the grid to center items in the main window
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Load images using CTkImage
        top_img = Image.open("src/images/logo.png")
        self.top_image = CTkImage(light_image=top_img, dark_image=top_img, size=(80, 80))

        bottom_img = Image.open("src/images/arrow.png")
        self.bottom_image = CTkImage(light_image=bottom_img, dark_image=bottom_img, size=(60, 60))

        # Create and place the top image
        self.top_image_label = CTkLabel(self, image=self.top_image, text="")
        self.top_image_label.grid(row=1, column=0)

        # Create and place the welcome label
        self.welcome_label = CTkLabel(self, text=self.translations["general"]["welcome_message"], font=("Inter", 24))
        self.welcome_label.grid(row=2, column=0)

        # Load icon for the label using CTkImage
        button_icon_img = Image.open("src/images/Card.png")
        self.button_icon = CTkImage(light_image=button_icon_img, dark_image=button_icon_img, size=(105, 90))

        # Create and place the scan card label with rounded corners
        self.scan_card_label = CTkLabel(
            self,
            image=self.button_icon,
            text=self.translations["general"]["scan_card_message"],
            compound="left",
            width=470,
            height=110,
            text_color="black",
            fg_color="white",
            font=("Inter", 24, "bold"),
            corner_radius=10 
        )
        self.scan_card_label.grid(row=3, column=0)

        # Create and place the bottom image
        self.bottom_image_label = CTkLabel(self, image=self.bottom_image, text="")
        self.bottom_image_label.grid(row=4, column=0)

        # Register the login callback
        self.nfc_reader.register_callback(self.login)

    def navigate_to_admin(self, user: User):
        self.destroy()
        self.gpio_controller.activate()
        try:
            user_count: int = User.get_count(self.session)
            item_count: int = Item.get_count(self.session)
            AdminMainFrame(
                self.parent,
                main_menu=KioskMainFrame,
                user=user,
                user_count=user_count,
                item_count=item_count,
            )
        finally:
            self.cleanup_resources()

    def navigate_to_customer(self, user: User):
        self.destroy()
        self.gpio_controller.activate()
        try:
            items: List[Item] = Item.read_all(self.session)
            UserMainPage(
                self.parent,
                main_menu=KioskMainFrame,
                user=user,
                items=items,
            )
        finally:
            self.cleanup_resources()

    def showUserNotFoundScreen(self):
        self.message = ShowMessage(
            self.parent,
            image="warning",
            heading=self.translations["user"]["account_not_detected"],
            text=self.translations["nfc"]["invalid_card_message"],
        )
        # Play negative sound when the user does not have valid ID
        if sound_controller:  # Check if the sound_controller is initialized
            logger.debug("Playing negative sound due to no valid ID")
            sound_controller.play_sound('negative')
        self.parent.after(5000, self.message.destroy)

    def login(self, current_id: str):
        if current_id:
            logger.info(f"Scanned NFC ID: {current_id}")
            user: User = User.get_by_nfcid(self.session, current_id)
            if user:
                self.handle_type(user)
            else:
                # Show warning message, "USER Not Found"
                self.showUserNotFoundScreen()
                logger.error("No user with this ID found")

    def handle_type(self, user: User):
        if user.type == self.translations["user"]["user"]:
            self.navigate_to_customer(user)
        elif user.type == self.translations["admin"]["admin"]:
            self.navigate_to_admin(user)

    def cleanup_resources(self):
        try:
            self.nfc_reader.stop()
        except Exception as e:
            logger.error(f"Error stopping NFC reader: {e}")