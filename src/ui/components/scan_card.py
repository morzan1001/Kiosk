from customtkinter import CTkButton, CTkFrame, CTkImage, CTkLabel
from PIL import Image

from src.localization.translator import get_translations
from src.logmgr import logger
from src.nfc_reader import NFCReader
from src.ui.components.heading_frame import HeadingFrame


class ScanCardFrame(CTkFrame):
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
            self, heading_text=heading_text, back_button_function=back_button_function
        )

        # Load images using CTkImage
        arrow_image = Image.open("src/images/arrow.png")
        self.bottom_image = CTkImage(light_image=arrow_image, dark_image=arrow_image)

        # Load icon for the button using CTkImage
        button_icon_image = Image.open("src/images/Card.png")
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
            hover=False,
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
            logger.info(f"Presented NFC-ID: {current_id}")
            self.set_nfcid_id(current_id)
            self.go_back_function()
        else:
            logger.info("Invalid card scanned!")
        # Stop the NFC reader once an ID has been processed
        self.nfc_reader.stop()
