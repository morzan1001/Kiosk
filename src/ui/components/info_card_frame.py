from io import BytesIO
from typing import Optional

from customtkinter import CTkFrame, CTkImage, CTkLabel
from PIL import Image


class InfoCardFrame(CTkFrame):
    """
    A generic frame for displaying an image (left) and two lines of text (right).
    Used for Items and Users in lists.
    """

    def __init__(
        self,
        master,
        title: str,
        subtitle: str,
        image_data: Optional[bytes] = None,
        image_path: Optional[str] = None,
        *args,
        **kwargs
    ):
        super().__init__(master, *args, **kwargs)

        # Image handling
        ctk_image = None
        if image_data:
            try:
                image_bytes = BytesIO(image_data)
                image_pil = Image.open(image_bytes)
                ctk_image = CTkImage(light_image=image_pil, dark_image=image_pil, size=(60, 60))
            except (OSError, ValueError):
                pass  # Fallback to empty
        elif image_path:
            try:
                image_pil = Image.open(image_path)
                ctk_image = CTkImage(light_image=image_pil, dark_image=image_pil, size=(60, 60))
            except (OSError, ValueError):
                pass

        # Image Label
        if ctk_image:
            image_label = CTkLabel(self, image=ctk_image, text="")
        else:
            image_label = CTkLabel(self, text="")

        image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Title (Top Line)
        title_label = CTkLabel(
            self,
            text=title,
            font=("Arial", 16, "bold"),
            text_color="black",
            anchor="s",
        )
        title_label.grid(row=0, column=1, sticky="sw", padx=10, pady=5)

        # Subtitle (Bottom Line)
        subtitle_label = CTkLabel(
            self,
            text=subtitle,
            font=("Arial", 14),
            text_color="black",
            anchor="n",
        )
        subtitle_label.grid(row=1, column=1, sticky="nw", padx=10, pady=5)
