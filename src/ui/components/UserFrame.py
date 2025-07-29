from customtkinter import CTkFrame, CTkLabel, CTkImage
from PIL import Image

from src.localization.translator import get_translations


class UserFrame(CTkFrame):
    def __init__(self, master, data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        user_id, user_name, user_credit = data

        self.translations = get_translations()
        # Load and display the image using CTkImage
        image = Image.open("src/images/user-big.png")
        ctk_image = CTkImage(light_image=image, dark_image=image, size=(60, 60))

        image_label = CTkLabel(self, image=ctk_image, text="")
        image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display user name and price
        user_label = CTkLabel(
            self,
            text=f"{user_name}",
            font=("Arial", 16, "bold"),
            text_color="black",
            anchor="s",
        )
        user_label.grid(row=0, column=1, sticky="sw", padx=10, pady=5)

        credit_label = CTkLabel(
            self,
            text=self.translations["user"]["credit_balance"].format(user_credit=user_credit),
            font=("Arial", 14),
            text_color="black",
            anchor="n",
        )
        credit_label.grid(row=1, column=1, sticky="nw", padx=10, pady=5)