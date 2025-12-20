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

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

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
        except Exception as e:
            logger.error(f"Error loading image {image_filename}: {e}")
            image_label = CTkLabel(self, text="[IMG]")
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display title
        title_label = CTkLabel(
            self,
            text=title,
            font=("Inter", 16, "bold"),
            anchor="s",
        )
        # If there is a value, title goes to top-right (row 0), else it centers or stays there
        title_row = 0
        title_sticky = "sw" if value else "w"

        title_label.grid(row=title_row, column=1, sticky=title_sticky, padx=10, pady=5)

        # Display value if present
        if value:
            value_label = CTkLabel(
                self,
                text=str(value),
                font=("Inter", 22, "bold"),
                anchor="n",
            )
            value_label.grid(row=1, column=1, sticky="nw", padx=10, pady=5)
