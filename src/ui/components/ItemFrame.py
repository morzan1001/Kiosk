from customtkinter import CTkFrame, CTkLabel, CTkImage
from PIL import Image
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
            
            # Create CTkImage with the same size as before (60x60)
            ctk_image = CTkImage(light_image=image_pil, dark_image=image_pil, size=(60, 60))

            image_label = CTkLabel(self, image=ctk_image, text="")
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