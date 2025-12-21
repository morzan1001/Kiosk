"""NFC scan prompt component."""

from customtkinter import CTkButton, CTkFrame, CTkImage, CTkLabel
from PIL import Image

from src.localization.translator import get_translations
from src.logmgr import logger
from src.nfc_reader import NFCReader
from src.ui.components.heading_frame import HeadingFrame
from src.utils.paths import get_image_path


class ScanCardFrame(CTkFrame):
    """Screen prompting the user to scan an NFC card."""

    def __init__(
        self,
        parent,
        heading_text: str,
        set_nfcid_id: str,
        back_button_function,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)

        self.nfc_reader = NFCReader()

        self.go_back_function = back_button_function
        self.parent = parent
        self.translations = get_translations()
        self.parent.title(self.translations["general"]["kiosk_title"])
        self.parent.geometry("800x480")
        self.set_nfcid_id: str = set_nfcid_id

        # Register the callback to be called when an NFC ID is read
        self.nfc_reader.register_callback(self.process_nfc_id)

        # Configure the grid to center items in the main window
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.heading_frame = HeadingFrame(
            self,
            heading_text=heading_text,
            back_button_function=back_button_function,
            width=760,
            fg_color="transparent",
        )
        self.heading_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="new")

        # Load images using CTkImage
        arrow_image = Image.open(get_image_path("arrow.png"))
        self.bottom_image = CTkImage(light_image=arrow_image, dark_image=arrow_image, size=(60, 60))

        # Load icon for the button using CTkImage
        button_icon_image = Image.open(get_image_path("Card.png"))
        self.button_icon = CTkImage(
            light_image=button_icon_image, dark_image=button_icon_image, size=(105, 90)
        )

        # Create and place the scan card button
        self.scan_card_button = CTkButton(
            self,
            image=self.button_icon,
            text=self.translations["general"]["scan_card_message"],
            compound="left",
            width=470,
            height=110,
            text_color="black",
            hover=False,
            fg_color="white",
            font=("Inter", 24, "bold"),
            border_spacing=0,
        )
        self.scan_card_button.grid(row=3, column=0)

        # Create and place the bottom image
        self.bottom_image_label = CTkLabel(self, image=self.bottom_image, text="")
        self.bottom_image_label.grid(row=4, column=0)

    def process_nfc_id(self, current_id: str):
        """
        Callback function to process the NFC ID.
        """
        if current_id:
            logger.info("Presented NFC-ID: %s", current_id)
            self.set_nfcid_id(current_id)
            self.go_back_function()
        else:
            logger.info("Invalid card scanned!")
        # Stop the NFC reader once an ID has been processed
        self.nfc_reader.stop()

    def stop_reader(self, timeout: float = 1.0) -> None:
        """Stop the background NFC reader thread.

        This is important when the scan screen is dismissed (e.g. user cancels/back).
        """
        try:
            if hasattr(self, "nfc_reader") and self.nfc_reader is not None:
                self.nfc_reader.stop(timeout=timeout)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Failed to stop NFC reader")
