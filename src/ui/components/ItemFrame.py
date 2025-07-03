from customtkinter import CTkFrame, CTkLabel
from PIL import Image, ImageTk
from io import BytesIO

class ItemFrame(CTkFrame):
    def __init__(self, master, data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Access item attributes directly
        item_image = data.image
        item_name = data.name
        item_price = data.price

        if item_image:
            # Create a BytesIO object from the image data
            image_bytes = BytesIO(item_image)

            # Open the image using Image.open
            image_pil = Image.open(image_bytes)
            image_pil = image_pil.resize((60, 60), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image_pil)

            image_label = CTkLabel(self, image=photo, text="")
            image_label.image = photo
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        else:
            image_label = CTkLabel(self, text="")
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display item name and price
        item_label = CTkLabel(
            self,
            text=f"{item_name}",
            font=("Arial", 16, "bold"),
            text_color="black",
            anchor="s",
        )
        item_label.grid(row=0, column=1, sticky="sw", padx=10, pady=5)

        price_label = CTkLabel(
            self,
            text=f"{item_price:.2f}€",
            font=("Arial", 14),
            text_color="black",
            anchor="n",
        )
        price_label.grid(row=1, column=1, sticky="nw", padx=10, pady=5)