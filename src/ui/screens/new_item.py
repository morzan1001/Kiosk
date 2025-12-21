from customtkinter import CTkButton, CTkFrame

from src.database import Item, get_db
from src.localization.translator import get_translations
from src.logmgr import logger
from src.ui.components.heading_frame import HeadingFrame
from src.ui.components.item_form import ItemForm
from src.ui.components.Message import ShowMessage


class AddNewItemFrame(CTkFrame):
    def __init__(self, parent, back_button_function, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Configure the grid for the frame
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.parent = parent
        self.back_button_function = back_button_function
        self.translations = get_translations()

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        # Heading Frame
        self.heading_frame = HeadingFrame(
            self,
            heading_text=self.translations["items"]["add_new_item"],
            back_button_function=self.back_button_function,
            width=760,
            fg_color="transparent",
        )
        self.heading_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="new")

        # Item Form
        self.item_form = ItemForm(self, parent_screen=self.parent)
        self.item_form.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Add Item Button
        self.add_item_button = CTkButton(
            self.item_form,
            text=self.translations["items"]["add_item"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.add_item,
        )
        self.add_item_button.grid(row=5, column=1, padx=(10, 20), pady=(5, 20), sticky="ew")

    def add_item(self):
        data = self.item_form.get_data()
        name = data["name"]
        price = data["price"]
        category = data["category"]
        quantity = data["quantity"]
        barcode = data["barcode"]
        file_path = data["file_path"]

        try:
            price = float(price)
        except ValueError:
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["items"]["error_adding_item"],
                text=self.translations["general"]["valid_number_price"],
            )
            self.parent.after(5000, self.message.destroy)
            return

        if not (name and price and category and barcode):
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["items"]["error_adding_item"],
                text=self.translations["general"]["fill_all_fields"],
            )
            self.parent.after(5000, self.message.destroy)
            return

        # Check if an item with the same barcode already exists
        existing_item = Item.get_by_barcode(self.session, barcode)
        if existing_item:
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["items"]["error_adding_item"],
                text=self.translations["items"]["barcode_already_exists"],
            )
            self.parent.after(5000, self.message.destroy)
            return

        # Read the image file as binary data
        image_data = None
        if file_path:
            try:
                with open(file_path, "rb") as file:
                    image_data = file.read()
            except (OSError, ValueError):
                image_data = None
                logger.exception("Failed to read selected image file: %s", file_path)
                self.message = ShowMessage(
                    self.parent,
                    image="unsuccessful",
                    heading=self.translations["items"]["error_adding_item"],
                    text=self.translations["general"]["image_read_failed"],
                )
                self.parent.after(5000, self.message.destroy)
                return

        # Create a new Item instance
        new_item = Item(
            name=name,
            price=price,
            category=category,
            quantity=quantity,
            barcode=barcode,
            image=image_data,
        )

        # Save the new item to the database
        new_item.create(self.session)

        self.back_button_function()
        return
