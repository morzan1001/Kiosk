"""Welcome/login screen.

Shows the kiosk start screen and handles NFC-based login, routing to either the
user or admin flow.
"""

from typing import List

from customtkinter import CTkFrame, CTkImage, CTkLabel
from PIL import Image

from src.database import Item, User, get_db
from src.localization.translator import get_translations
from src.lock.gpio_manager import get_gpio_controller
from src.logmgr import logger
from src.nfc_reader import NFCReader
from src.sounds.sound_manager import get_sound_controller
from src.ui.components.Message import ShowMessage
from src.ui.navigation import clear_root
from src.ui.screens.admin_main import AdminMainFrame
from src.ui.screens.user_main import UserMainPage
from src.utils.paths import get_image_path


class KioskMainFrame(CTkFrame):
    """Main kiosk frame shown at application startup."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.translations = get_translations()
        self.nfc_reader = NFCReader()
        self.session = get_db()
        self.gpio_controller = get_gpio_controller()
        self.sound_controller = get_sound_controller()

        self.parent = parent
        self.parent.title(self.translations["general"]["kiosk_title"])
        self.parent.geometry("800x480")
        self.configure(fg_color="transparent")

        # Configure the grid to center items in the main window
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_img = Image.open(get_image_path("logo.png"))
        self.top_image = CTkImage(light_image=top_img, dark_image=top_img, size=(80, 80))

        bottom_img = Image.open(get_image_path("arrow.png"))
        self.bottom_image = CTkImage(light_image=bottom_img, dark_image=bottom_img, size=(60, 60))

        self.top_image_label = CTkLabel(self, image=self.top_image, text="")
        self.top_image_label.grid(row=1, column=0)

        self.welcome_label = CTkLabel(
            self,
            text=self.translations["general"]["welcome_message"],
            font=("Inter", 24),
        )
        self.welcome_label.grid(row=2, column=0)

        button_icon_img = Image.open(get_image_path("Card.png"))
        self.button_icon = CTkImage(
            light_image=button_icon_img, dark_image=button_icon_img, size=(105, 90)
        )

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
            corner_radius=10,
        )
        self.scan_card_label.grid(row=3, column=0)

        self.bottom_image_label = CTkLabel(self, image=self.bottom_image, text="")
        self.bottom_image_label.grid(row=4, column=0)

        self.nfc_reader.register_callback(self.login)

    def navigate_to_admin(self, user: User):
        self.gpio_controller.activate()
        try:
            clear_root(self.parent)
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
        self.gpio_controller.activate()
        try:
            clear_root(self.parent)
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
        if self.sound_controller:
            logger.debug("Playing negative sound due to no valid ID")
            self.sound_controller.play_sound("negative")
        self.parent.after(5000, self.message.destroy)

    def login(self, current_id: str):
        # Schedule the processing on the main thread to ensure thread safety for UI updates
        self.after(0, lambda: self._process_login(current_id))

    def _process_login(self, current_id: str):
        if current_id:
            logger.info("Scanned NFC ID: %s", current_id)
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
        except (AttributeError, OSError, RuntimeError):  # pragma: no cover
            # NFC shutdown can fail depending on hardware/driver state; we only log.
            logger.exception("Error stopping NFC reader")
