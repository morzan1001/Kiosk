from io import BytesIO

from customtkinter import (CTkButton, CTkEntry, CTkFrame, CTkImage, CTkLabel,
                           CTkOptionMenu, filedialog)
from PIL import Image

from src.database import Item, get_db
from src.localization.translator import get_translations
from src.ui.components.barcode import AddBarcodeFrame
from src.ui.components.change_quantity_frame import ChangeQuantityFrame
from src.ui.components.confirmation import DeleteConfirmation
from src.ui.components.heading_frame import HeadingFrame
from src.ui.components.message import ShowMessage


class UpdateItemFrame(CTkFrame):
    def __init__(self, parent, back_button_function, item_id: int, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.item_id: int = item_id
        self.back_button_function = back_button_function
        self.translations = get_translations()
        self.barcode: str = ""

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        # Configure the grid for the frame
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Heading Frame
        heading_frame = HeadingFrame(
            self,
            heading_text=self.translations["items"]["update_item"],
            back_button_function=back_button_function,
            delete_button_function=self.delete_item,
            width=600,
            fg_color="transparent",
        )
        heading_frame.grid(row=0, column=0, columnspan=2, padx=90, sticky="new")

        # Load the image using CTkImage
        upload_image = Image.open("src/images/upload.png")
        self.upload_image = CTkImage(
            light_image=upload_image, dark_image=upload_image, size=(80, 80)
        )

        # Image Button
        self.update_button = CTkButton(
            self,
            image=self.upload_image,
            width=165,
            height=120,
            text="",
            command=self.upload_image_button_pressed,
        )
        self.update_button.grid(row=1, column=0, columnspan=2, pady=(20, 10))

        # Inventory Label
        self.inventory_label = CTkLabel(
            self,
            text=self.translations["items"]["inventory_label"],
            width=290,
            anchor="w",
            font=("Arial", 18, "bold"),
        )
        self.inventory_label.grid(row=2, column=1, pady=(10, 0))

        # Name Entry
        self.name_entry = CTkEntry(
            self,
            placeholder_text=self.translations["items"]["item_name"],
            width=290,
            height=50,
            corner_radius=10,
            font=("Inter", 18, "bold"),
        )
        self.name_entry.grid(row=3, column=0, padx=(20, 10))

        # Inventory Frame
        self.inventory_frame = ChangeQuantityFrame(
            self,
            width=290,
            height=60,
            corner_radius=10,
            border_width=2,
        )
        self.inventory_frame.grid(
            row=3, column=1, padx=(10, 20), pady=(10, 10), sticky="w"
        )

        # Price Entry
        self.price_entry = CTkEntry(
            self,
            placeholder_text=self.translations["items"]["enter_price"],
            width=290,
            height=50,
            corner_radius=10,
            font=("Inter", 18, "bold"),
        )
        self.price_entry.grid(row=4, column=0, padx=(20, 10), pady=(10, 10))
        self.price_entry.bind("<KeyRelease>", self.validate_price_input)

        # Category Dropdown
        self.category_dropdown = CTkOptionMenu(
            self,
            values=[
                self.translations["items"]["drinks"],
                self.translations["items"]["snacks"],
            ],
            width=290,  # Gleiche Breite wie die anderen Felder
            height=50,
            font=("Inter", 18, "bold"),
            dropdown_font=("Inter", 18, "bold"),
        )
        self.category_dropdown.grid(
            row=4, column=1, padx=(10, 20), pady=(10, 10), sticky="w"
        )

        # Update Barcode Button
        self.update_barcode_button = CTkButton(
            self,
            text=self.translations["items"]["update_barcode"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.show_barcode,
        )
        self.update_barcode_button.grid(row=5, column=0, padx=(20, 10), pady=(20, 10))

        # Add Item Button
        self.update_item_button = CTkButton(
            self,
            text=self.translations["items"]["update_item"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.update_item,
        )
        self.update_item_button.grid(row=5, column=1, padx=(10, 20), pady=(20, 10))
        self.initialize_item()

    def initialize_item(self):
        item = Item.get_by_id(self.session, self.item_id)
        name = item.name
        price = item.price
        image = item.image
        self.barcode = item.barcode
        quantity = str(item.quantity)

        self.name_entry.insert(0, name)
        self.price_entry.insert(0, price)
        self.inventory_frame.set_entry_text(quantity)

        if image:
            # Create a BytesIO object from the image data
            image_bytes = BytesIO(image)

            # Open the image using Image.open
            image_pil = Image.open(image_bytes)
            # Create CTkImage with the loaded image at size 100x100
            photo = CTkImage(
                light_image=image_pil, dark_image=image_pil, size=(100, 100)
            )
            self.update_button.configure(image=photo)

    def upload_image_button_pressed(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            self.upload_image_tk = Image.open(file_path)
            self.file_path = file_path
            # Create CTkImage with the uploaded image at size 100x100
            uploaded_image = CTkImage(
                light_image=self.upload_image_tk,
                dark_image=self.upload_image_tk,
                size=(100, 100),
            )
            self.update_button.configure(image=uploaded_image)

    def confirm_barcode(self):
        self.barcode = self.barcode_frame.get()
        if self.barcode:
            self.barcode = str(self.barcode)
        self.barcode_frame.grab_release()
        self.barcode_frame.destroy()

    def show_barcode(self):
        self.barcode_frame = AddBarcodeFrame(self.parent, self.confirm_barcode)
        self.after(
            100, self.barcode_frame.grab_set
        )  # Call grab_set after a short delay

    def validate_price_input(self, event=None):
        """Validate price input to ensure it's a valid number"""
        current_value = self.price_entry.get()

        # Allow empty field
        if not current_value:
            return True

        # Check if it's a valid price format (e.g., 1.99, 10, 0.50)
        try:
            price = float(current_value)
            if price < 0:
                self.price_entry.delete(0, "end")
                return False
            # Limit to 2 decimal places
            formatted_price = f"{price:.2f}"
            if current_value != formatted_price:
                self.price_entry.delete(0, "end")
                self.price_entry.insert(0, formatted_price)
        except ValueError:
            # Remove invalid character
            self.price_entry.delete(0, "end")
            return False

        return True

    def update_item(self):
        # Get data from entries and option menu
        name = self.name_entry.get()
        price = self.price_entry.get()
        category = self.category_dropdown.get()
        quantity = int(self.inventory_frame.get())
        barcode = self.barcode

        if not (name and price and category and barcode):
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["items"]["error_updating_item"],
                text=self.translations["general"]["fill_all_fields"],
            )
            self.parent.after(5000, self.message.destroy)
            return

        # Get image data
        image_data = None
        if hasattr(self, "file_path"):
            with open(self.file_path, "rb") as file:
                image_data = file.read()

        # Fetch the item by ID
        item_instance = Item.get_by_id(self.session, self.item_id)

        # Update the item instance with new values if it exists
        if item_instance:
            item_instance.update(
                self.session,
                name=name,
                price=price,
                quantity=quantity,
                category=category,
                image=image_data,
                barcode=barcode,
            )

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
