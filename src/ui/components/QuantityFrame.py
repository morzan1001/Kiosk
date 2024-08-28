from customtkinter import *
from PIL import Image, ImageTk

class QuantityFrame(CTkFrame):
    def __init__(self, master, data, update_total_price, item_price, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Set the textvariable
        self.data = data
        self.update_total_price = update_total_price
        self.item_price = item_price

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0), weight=1)

        # Load images for buttons
        add_image = Image.open("src/images/add.png")
        add_image = add_image.resize((30, 30), Image.Resampling.LANCZOS)
        self.add_photo = ImageTk.PhotoImage(add_image)

        minus_image = Image.open("src/images/minus.png")
        minus_image = minus_image.resize((30, 30), Image.Resampling.LANCZOS)
        self.minus_photo = ImageTk.PhotoImage(minus_image)

        # Create and place the decrement button
        self.decrement_button = CTkButton(
            self,
            image=self.minus_photo,
            width=10,
            height=10,
            text="",
            command=self.decrement,
            fg_color="transparent",
            hover=False,
        )
        self.decrement_button.grid(row=0, column=0, padx=(10, 0))

        # Create and place the entry
        vcmd = (self.register(self.validate_entry), '%P')  # Validation command
        self.entry = CTkEntry(
            self,
            textvariable=self.data,
            width=50,
            justify="center",
            fg_color="transparent",
            border_width=0,
            font=("Arial", 16, "bold"),
            text_color="black",
            validate="key",
            validatecommand=vcmd,
        )
        self.entry.grid(row=0, column=1)

        # Create and place the increment button
        self.increment_button = CTkButton(
            self,
            image=self.add_photo,
            width=10,
            height=10,
            text="",
            command=self.increment,
            fg_color="transparent",
            hover=False,
        )
        self.increment_button.grid(row=0, column=2, padx=(0, 10))

    def increment(self):
        try:
            value = self.data.get()
        except:
            value = 0
        if value < 999:
            self.data.set(value + 1)
            self.update_total_price()

    def decrement(self):
        try:
            value = self.data.get()
        except:
            value = 0
        if value > 0:
            self.data.set(value - 1)
            self.update_total_price()

    def validate_entry(self, new_value):
        if new_value == "":
            return False
        elif int(new_value) > 999:
            return False
        
        # Check if the new value is a digit
        if new_value.isdigit():
            return True
        else:
            return False
