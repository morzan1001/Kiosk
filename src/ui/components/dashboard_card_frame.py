"""Admin dashboard card component."""

import tkinter as tk
from typing import Optional

from customtkinter import CTkFrame, CTkImage, CTkLabel
from PIL import Image

from src.logmgr import logger
from src.utils.paths import get_image_path


class DashboardCardFrame(CTkFrame):
    """
    A unified card for the admin dashboard.
    Displays an icon (left), a title, and an optional value (right).
    """

    def __init__(
        self,
        master,
        title: str,
        image_filename: str,
        value: Optional[str] = None,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)

        # Keep the card at the explicit width/height passed in (admin dashboard wants equal cards).
        self.grid_propagate(False)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Compute a reasonable wrap length based on the configured width.
        try:
            card_width = int(self.cget("width"))
        except (tk.TclError, TypeError, ValueError):
            card_width = 270
        title_wrap = max(120, card_width - 120)

        # Load and display the image
        try:
            # Ensure filename has extension if missing (legacy support)
            if not image_filename.endswith(".png"):
                image_filename += ".png"

            img_path = get_image_path(image_filename)
            img = Image.open(img_path)
            ctk_image = CTkImage(light_image=img, dark_image=img, size=(80, 80))

            image_label = CTkLabel(self, image=ctk_image, text="")
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        except (OSError, ValueError) as e:
            logger.error("Error loading image %s: %s", image_filename, e)
            image_label = CTkLabel(self, text="[IMG]")
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display title
        title_label = CTkLabel(
            self,
            text=title,
            font=("Inter", 16, "bold"),
            text_color="black",
            anchor="w",
            justify="left",
            wraplength=title_wrap,
        )
        if value:
            # Title above, value below.
            title_label.grid(row=0, column=1, sticky="sw", padx=10, pady=(10, 2))
        else:
            # No value: center the title vertically by spanning both rows.
            title_label.grid(row=0, column=1, rowspan=2, sticky="w", padx=10)

        # Display value if present
        if value:
            value_label = CTkLabel(
                self,
                text=str(value),
                font=("Inter", 22, "bold"),
                text_color="black",
                anchor="n",
            )
            value_label.grid(row=1, column=1, sticky="nw", padx=10, pady=(2, 10))
