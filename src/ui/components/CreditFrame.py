from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton, StringVar
from PIL import Image, ImageTk

class CreditFrame(CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Load images for buttons
        self.credit_image = Image.open("src/images/credit.png")
        self.credit_image = ImageTk.PhotoImage(self.credit_image)

        self.minus_image = Image.open("src/images/minus.png")
        self.minus_image = ImageTk.PhotoImage(self.minus_image)

        self.add_image = Image.open("src/images/add.png")
        self.add_image = ImageTk.PhotoImage(self.add_image)

        self.credit_label = CTkLabel(
            self, text="", width=40, height=40, image=self.credit_image
        )
        self.credit_label.grid(row=0, column=0, padx=(10, 0))

        vcmd = (self.register(self.validate_entry), "%P")  # Validation command
        self.data = StringVar(value="0")

        # Entry field
        self.entry = CTkEntry(
            self,
            textvariable=self.data,
            width=145,
            height=30,
            fg_color="#1C1C1C",
            text_color="white",
            font=("Inter", 18, "bold"),
            border_width=0,
            validate="key",
            validatecommand=vcmd,
        )
        self.entry.grid(row=0, column=1, padx=(10, 5))

        # Minus button
        self.minus_button = CTkButton(
            self,
            text="",
            image=self.minus_image,
            width=30,
            height=30,
            fg_color="#1C1C1C",
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
            fg_color="#1C1C1C",
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
