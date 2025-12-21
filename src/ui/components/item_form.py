from io import BytesIO
from typing import Optional

from customtkinter import (
    CTkButton,
    CTkEntry,
    CTkFrame,
    CTkImage,
    CTkLabel,
    CTkOptionMenu,
    filedialog,
)
from PIL import Image

from src.localization.translator import get_translations
from src.ui.components.Barcode import AddBarcodeFrame
from src.ui.components.change_quantity_frame import ChangeQuantityFrame
from src.utils.paths import get_image_path


class ItemForm(CTkFrame):
    def __init__(self, master, parent_screen, show_inventory_icon: bool = False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.parent_screen = parent_screen
        self.translations = get_translations()
        self.barcode: str = ""
        self.file_path: Optional[str] = None

        self.grid_columnconfigure((0, 1), weight=1)
        # Row 0: Image (fixed)
        # Row 1: Label (fixed)
        # Row 2: Name + Inventory (fixed)
        # Row 3: Price + Category (fixed)
        # Row 4: Spacer (flex)
        # Row 5: Buttons (fixed)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=0)

        self.configure(fg_color="transparent")

        # Load the image using CTkImage
        upload_image_path = get_image_path("upload.png")
        upload_image = Image.open(upload_image_path)
        self.upload_image = CTkImage(
            light_image=upload_image, dark_image=upload_image, size=(80, 80)
        )

        # Image Button
        self.image_button = CTkButton(
            self,
            image=self.upload_image,
            width=165,
            height=120,
            text="",
            fg_color="white",
            hover_color="#ddd",
            command=self.upload_image_button_pressed,
        )
        self.image_button.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="n")

        # Inventory Label
        self.inventory_label = CTkLabel(
            self,
            text=self.translations["items"]["inventory_label"],
            width=290,
            anchor="w",
            font=("Arial", 18, "bold"),
            text_color="white",
        )
        self.inventory_label.grid(row=1, column=1, padx=(10, 20), pady=(10, 0), sticky="sw")

        # Name Entry
        self.name_entry = CTkEntry(
            self,
            placeholder_text=self.translations["items"]["item_name"],
            width=290,
            height=50,
            corner_radius=10,
            font=("Inter", 18, "bold"),
        )
        self.name_entry.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        # Inventory Frame
        self.inventory_frame = ChangeQuantityFrame(
            self,
            icon_name=("item.png" if show_inventory_icon else None),
            width=290,
            height=50,
            fg_color="#1C1C1C",
            corner_radius=10,
            border_width=2,
            border_color="#5D5D5D",
        )
        self.inventory_frame.grid(row=2, column=1, padx=(10, 20), pady=(10, 10), sticky="ew")

        # Price Entry
        self.price_entry = CTkEntry(
            self,
            placeholder_text=self.translations["items"]["enter_price"],
            width=290,
            height=50,
            corner_radius=10,
            font=("Inter", 18, "bold"),
        )
        self.price_entry.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        # Category Dropdown
        self.category_dropdown = CTkOptionMenu(
            self,
            values=[
                self.translations["items"]["drinks"],
                self.translations["items"]["snacks"],
            ],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            dropdown_fg_color="#2B2B2B",
            dropdown_text_color="white",
            dropdown_hover_color="#575757",
            dropdown_font=("Inter", 18, "bold"),
        )
        self.category_dropdown.grid(row=3, column=1, padx=(10, 20), pady=(10, 10), sticky="ew")

        # Barcode Button
        self.barcode_button = CTkButton(
            self,
            text=self.translations["items"]["add_barcode"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.show_barcode,
        )
        self.barcode_button.grid(row=5, column=0, padx=(20, 10), pady=(5, 20), sticky="ew")

    def upload_image_button_pressed(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            self.file_path = file_path
            image_pil = Image.open(file_path)
            # Create CTkImage with the uploaded image at size 100x100
            uploaded_image = CTkImage(
                light_image=image_pil,
                dark_image=image_pil,
                size=(100, 100),
            )
            self.image_button.configure(image=uploaded_image)

    def confirm_barcode(self):
        self.barcode = self.barcode_frame.get()
        if self.barcode:
            self.barcode = str(self.barcode)
        self.barcode_frame.grab_release()
        self.barcode_frame.destroy()

    def show_barcode(self):
        # AddBarcodeFrame is a CTkToplevel (separate window), so no grid/pack needed
        # It positions itself using geometry in its __init__
        # Use winfo_toplevel() to get the root window for CTkToplevel
        root = self.winfo_toplevel()
        self.barcode_frame = AddBarcodeFrame(root, self.confirm_barcode)
        # Call grab_set after a short delay to ensure the window is fully rendered
        self.after(100, self.barcode_frame.grab_set)

    def get_data(self):
        return {
            "name": self.name_entry.get(),
            "price": self.price_entry.get(),
            "category": self.category_dropdown.get(),
            "quantity": self.inventory_frame.get(),
            "barcode": self.barcode,
            "file_path": self.file_path,
        }

    def set_data(self, name, price, quantity, barcode, category=None, image_data=None):
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, name)

        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, price)

        self.inventory_frame.set_entry_text(str(quantity))

        self.barcode = barcode

        if category:
            self.category_dropdown.set(category)

        if image_data:
            image_bytes = BytesIO(image_data)
            image_pil = Image.open(image_bytes)
            photo = CTkImage(light_image=image_pil, dark_image=image_pil, size=(100, 100))
            self.image_button.configure(image=photo)
