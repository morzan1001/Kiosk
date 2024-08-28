from src.localization.translator import get_translations
from src.nfc_reader import NFC_READER
from src.logmgr import logger
from customtkinter import *
from PIL import Image, ImageTk
from src.ui.components.HeadingFrame import HeadingFrame

class ScanCardFrame(CTkFrame):
    def __init__(
        self,
        parent,
        heading_text,
        set_nfcid_id,
        back_button_function,
        *args,
        **kwargs
    ):
        super().__init__(parent, *args, **kwargs)

        self.nfc_reader = NFC_READER()

        self.go_back_function = back_button_function
        self.parent = parent
        self.translations = get_translations()
        self.parent.title(self.translations["general"]["kiosk_title"])
        self.parent.geometry("800x480")
        self.set_nfcid_id = set_nfcid_id
        

        # Register the callback to be called when an NFC ID is read
        self.nfc_reader.register_callback(self.process_nfc_id)

        # Configure the grid to center items in the main window
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.heading_frame = HeadingFrame(
            self, heading_text=heading_text, back_button_function=back_button_function
        )

        # Load images
        self.bottom_image = Image.open("src/images/arrow.png")
        self.bottom_image = ImageTk.PhotoImage(self.bottom_image)

        # Load icon for the button
        button_icon = Image.open("src/images/Card.png")
        button_icon = button_icon.resize((105, 90), Image.Resampling.LANCZOS)
        self.button_icon = ImageTk.PhotoImage(button_icon)

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
            border_spacing=0
        )
        self.scan_card_button.grid(row=3, column=0)

        # Create and place the bottom image
        self.bottom_image_label = CTkLabel(self, image=self.bottom_image, text="")
        self.bottom_image_label.grid(row=4, column=0)

    def process_nfc_id(self, current_id):
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