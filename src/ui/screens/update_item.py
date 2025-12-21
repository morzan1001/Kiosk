from customtkinter import CTkButton, CTkFrame

from src.database import Item, get_db
from src.localization.translator import get_translations
from src.ui.components.Confirmation import DeleteConfirmation
from src.ui.components.heading_frame import HeadingFrame
from src.ui.components.item_form import ItemForm
from src.ui.components.Message import ShowMessage


class UpdateItemFrame(CTkFrame):
    def __init__(self, parent, back_button_function, item_id: int, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.item_id: int = item_id
        self.back_button_function = back_button_function
        self.translations = get_translations()

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        # Configure the grid for the frame
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # Heading Frame
        heading_frame = HeadingFrame(
            self,
            heading_text=self.translations["items"]["update_item"],
            back_button_function=back_button_function,
            delete_button_function=self.delete_item,
            width=760,
            fg_color="transparent",
        )
        heading_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="new")

        # Item Form
        self.item_form = ItemForm(self, parent_screen=self.parent, show_inventory_icon=True)
        self.item_form.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.item_form.barcode_button.configure(text=self.translations["items"]["update_barcode"])

        # Update Item Button
        self.update_item_button = CTkButton(
            self.item_form,
            text=self.translations["items"]["update_item"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.update_item,
        )
        self.update_item_button.grid(row=5, column=1, padx=(10, 20), pady=(5, 20), sticky="ew")

        self.initialize_item()

    def initialize_item(self):
        item = Item.get_by_id(self.session, self.item_id)
        if item:
            self.item_form.set_data(
                name=item.name,
                price=item.price,
                quantity=item.quantity,
                barcode=item.barcode,
                image_data=item.image,
                category=item.category,
            )

    def update_item(self):
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
                heading=self.translations["items"]["error_updating_item"],
                text=self.translations["general"]["valid_number_price"],
            )
            self.parent.after(5000, self.message.destroy)
            return

        if not (name and price and category and barcode):
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["items"]["error_updating_item"],
                text=self.translations["general"]["fill_all_fields"],
            )
            self.parent.after(5000, self.message.destroy)
            return

        # Check if another item with the same barcode already exists
        existing_item = Item.get_by_barcode(self.session, barcode)
        if existing_item and existing_item.id != self.item_id:
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["items"]["error_updating_item"],
                text=self.translations["items"]["barcode_already_exists"],
            )
            self.parent.after(5000, self.message.destroy)
            return

        # Read the image file as binary data if a new file was selected
        image_data = None
        if file_path:
            with open(file_path, "rb") as file:
                image_data = file.read()

        # Update the item in the database
        item = Item.get_by_id(self.session, self.item_id)
        if item:
            update_kwargs = {
                "name": name,
                "price": price,
                "category": category,
                "quantity": quantity,
                "barcode": barcode,
            }
            if image_data:
                update_kwargs["image"] = image_data

            item.update(self.session, **update_kwargs)

        self.back_button_function()

    def confirm_delete(self):
        # Fetch the item by ID
        item_instance = Item.get_by_id(self.session, self.item_id)

        # If the item exists, delete the user
        if item_instance:
            item_instance.delete(self.session)

        self.back_button_function()

    def delete_item(self):
        DeleteConfirmation(self.parent, self.confirm_delete, "item")
