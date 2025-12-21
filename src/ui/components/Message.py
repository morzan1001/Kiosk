"""Transient message overlay component."""

import os

from customtkinter import CTkFrame, CTkImage, CTkLabel
from PIL import Image

from src.logmgr import logger
from src.utils.paths import get_image_path


class ShowMessage(CTkFrame):
    """Simple message frame with icon, heading and text."""

    def __init__(self, root, image, heading: str, text: str, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        # Create the main frame
        self.main_frame = self
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid for main frame
        self.main_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Load the image
        try:
            # Ensure filename has extension if missing (legacy support)
            if isinstance(image, str):
                _, ext = os.path.splitext(os.path.basename(image))
                if not ext:
                    image += ".png"

            img_path = get_image_path(image)
            img = Image.open(img_path)
            ctk_image = CTkImage(light_image=img, dark_image=img, size=(80, 80))

            self.image_label = CTkLabel(self.main_frame, image=ctk_image, text="")
            self.image_label.grid(row=2, column=0, pady=10, padx=10, sticky="s")
        except (OSError, ValueError) as e:
            logger.error("Error loading image %s: %s", image, e)
            self.image_label = CTkLabel(self.main_frame, text="[IMG]")
            self.image_label.grid(row=2, column=0, pady=10, padx=10, sticky="s")

        # Warning text
        self.warning_label = CTkLabel(
            self.main_frame,
            text=heading,
            font=("Inter", 30, "bold"),
            text_color="white",
        )
        self.warning_label.grid(row=3, column=0, pady=10, padx=10, sticky="s")

        # Additional text
        self.additional_text_label = CTkLabel(
            self.main_frame, text=text, font=("Inter", 20), text_color="white"
        )
        self.additional_text_label.grid(row=4, column=0, pady=10, padx=10, sticky="n")
