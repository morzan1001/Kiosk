from customtkinter import CTkButton, CTkFrame, CTkImage, CTkLabel
from PIL import Image

from src.utils.paths import get_image_path


class HeadingFrame(CTkFrame):
    def __init__(
        self,
        parent,
        heading_text: str,
        back_button_function,
        delete_button_function=None,
        *args,
        **kwargs
    ):
        super().__init__(parent, *args, **kwargs)

        # Configure the frame
        self.configure(fg_color="transparent")
        self.grid(row=0, column=0, sticky="new", padx=50, pady=20)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Load the back button image using CTkImage
        back_image = Image.open(get_image_path("back.png"))
        self.back_image = CTkImage(
            light_image=back_image, dark_image=back_image, size=(42, 32)
        )

        # Create the back button
        self.back_button = CTkButton(
            self,
            text="",
            image=self.back_image,
            width=42,
            height=32,
            fg_color="transparent",
            hover=False,
            command=back_button_function,
        )
        self.back_button.grid(row=0, column=0, sticky="w")

        # Create the heading label
        self.heading_label = CTkLabel(
            self,
            text=heading_text,
            font=("Inter", 24, "bold"),
        )
        self.heading_label.grid(row=0, column=1)

        if delete_button_function:
            # Load the delete button image using CTkImage
            delete_image = Image.open(get_image_path("delete.png"))
            self.delete_image = CTkImage(
                light_image=delete_image, dark_image=delete_image, size=(30, 35)
            )

            # Create the delete button
            self.delete_button = CTkButton(
                self,
                text="",
                image=self.delete_image,
                width=30,
                height=35,
                fg_color="transparent",
                hover=False,
                command=delete_button_function,
            )
            self.delete_button.grid(row=0, column=2, sticky="e")
