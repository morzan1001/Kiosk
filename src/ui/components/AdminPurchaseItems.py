from customtkinter import CTkFrame, CTkLabel, CTkImage
from PIL import Image

class AdminPurchaseItemsFrame(CTkFrame):
    def __init__(self, master, image, heading: str, data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # Load and display the image
        img = Image.open(f"src/images/{image}.png")
        ctk_image = CTkImage(light_image=img, dark_image=img, size=(80, 80))
        
        image_label = CTkLabel(self, image=ctk_image, text="")
        image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Display item name and quantity
        heading_label = CTkLabel(
            self,
            text=heading,
            font=("Inter", 16, "bold"),
            text_color="black",
            anchor="s",
        )
        heading_label.grid(row=0, column=1, sticky="sw", padx=10, pady=5)
