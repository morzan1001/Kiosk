from customtkinter import *
from PIL import Image, ImageTk

class AdminPurchaseItemsFrame(CTkFrame):
    def __init__(self, master, image, heading, data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # Load and display the image
        image = Image.open(f"src/images/{image}.png")
        image = image.resize((80, 80), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        image_label = CTkLabel(self, image=photo, text="")
        image_label.image = photo
        image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display item name and quantity
        heading_label = CTkLabel(
            self,
            text=heading,
            font=("Inter", 16, "bold"),
            text_color="black",
            anchor="s",
        )
        heading_label.grid(row=0, column=1, sticky="sw", padx=10, pady=5)
