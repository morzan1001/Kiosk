from customtkinter import *
from tkinter import *
from PIL import Image, ImageTk


class ShowMessage(CTkFrame):
    def __init__(self, root, image, heading, text, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        # Create the main frame
        self.main_frame = self
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid for main frame
        self.main_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Load the image
        self.image = Image.open(f"src/images/{image}.png")
        self.image = self.image.resize((80, 80), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(self.image)

        # Image Label
        self.image_label = CTkLabel(self.main_frame, image=self.image, text="")
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