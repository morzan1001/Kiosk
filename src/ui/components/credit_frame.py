from customtkinter import CTkButton, CTkEntry, CTkFrame, CTkImage, CTkLabel, StringVar
from PIL import Image

from src.utils.paths import get_image_path


class CreditFrame(CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Layout: [icon][entry........][minus][plus]
        # Only the entry column should expand, so the icon stays at the far left.
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # Load images for buttons using CTkImage
        credit_img = Image.open(get_image_path("credit.png"))
        self.credit_image = CTkImage(light_image=credit_img, dark_image=credit_img, size=(40, 40))

        minus_img = Image.open(get_image_path("minus.png"))
        self.minus_image = CTkImage(light_image=minus_img, dark_image=minus_img, size=(30, 30))

        add_img = Image.open(get_image_path("add.png"))
        self.add_image = CTkImage(light_image=add_img, dark_image=add_img, size=(30, 30))

        self.credit_label = CTkLabel(self, text="", width=40, height=40, image=self.credit_image)
        self.credit_label.grid(row=0, column=0, padx=(10, 0), sticky="w")

        vcmd = (self.register(self.validate_entry), "%P")  # Validation command
        self.data = StringVar(value="0")

        # Entry field
        self.entry = CTkEntry(
            self,
            textvariable=self.data,
            width=145,
            height=30,
            fg_color="transparent",
            text_color="white",
            font=("Inter", 18, "bold"),
            border_width=0,
            validate="key",
            validatecommand=vcmd,
        )
        self.entry.grid(row=0, column=1, padx=(10, 5), sticky="ew")

        # Minus button
        self.minus_button = CTkButton(
            self,
            text="",
            image=self.minus_image,
            width=30,
            height=30,
            fg_color="transparent",
            hover=False,
            command=self.decrease_number,
        )
        self.minus_button.grid(row=0, column=2, padx=(5, 0), pady=(10, 10), sticky="e")

        # Plus button
        self.add_button = CTkButton(
            self,
            text="",
            image=self.add_image,
            width=30,
            height=30,
            fg_color="transparent",
            hover=False,
            command=self.increase_number,
        )
        self.add_button.grid(row=0, column=3, padx=(0, 10), pady=(10, 10), sticky="w")

    def set_entry_text(self, text):
        self.data.set(str(text))

    # Function to increase the number
    def increase_number(self):
        current_value = self.get_int_value()
        if current_value < 999:
            self.data.set(str(current_value + 1))

    # Function to decrease the number
    def decrease_number(self):
        current_value = self.get_int_value()
        if current_value > 0:
            self.data.set(str(current_value - 1))

    def validate_entry(self, new_value):
        try:
            if new_value == "":
                return False
            # Strip leading zeros
            new_value = new_value.lstrip("0") or "0"

            # Check if the new value is a digit and within the range
            if new_value.isdigit() and 0 <= int(new_value):
                return True
            else:
                return False
        except ValueError:
            return False

    def get(self):
        return self.entry.get()

    def get_int_value(self):
        try:
            return float(self.data.get())
        except ValueError:
            return 0
