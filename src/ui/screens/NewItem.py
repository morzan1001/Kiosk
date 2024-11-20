from customtkinter import *
from PIL import Image, ImageTk
from src.localization.translator import get_translations
from src.ui.components.HeadingFrame import HeadingFrame
from src.ui.components.Barcode import AddBarcodeFrame
from src.ui.components.ChangeQuantityFrame import ChangeQuantityFrame
from src.ui.components.Message import ShowMessage
from src.database import get_db, Item


class AddNewItemFrame(CTkFrame):
    def __init__(self, parent, back_button_function, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Configure the grid for the frame
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.barcode: str = ""
        self.parent = parent
        self.back_button_function = back_button_function
        self.translations = get_translations()

        self.session = get_db()

        # Heading Frame
        self.heading_frame = HeadingFrame(
            self, self.translations["items"]["add_new_item"], back_button_function=self.back_button_function
        )
        self.heading_frame.grid(row=0, column=0, columnspan=2, padx=40)

        self.configure(width=800, height=480, fg_color="transparent")

        # Load the image
        self.upload_image = Image.open("src/images/upload.png")
        self.upload_image = self.upload_image.resize((80, 80), Image.Resampling.LANCZOS)
        self.upload_image = ImageTk.PhotoImage(self.upload_image)

        # Image Button
        self.update_button = CTkButton(
            self,
            image=self.upload_image,
            width=165,
            height=120,
            text="",
            fg_color="white",
            hover_color="#ddd",
            command=self.upload_image_button_pressed,
        )
        self.update_button.grid(row=1, column=0, columnspan=2, pady=(20, 10))

        # Inventory Label
        self.inventory_label = CTkLabel(
            self,
            text=self.translations["items"]["inventory_label"],
            width=290,
            anchor="w",
            text_color="white",
            font=("Arial", 18, "bold"),
        )
        self.inventory_label.grid(row=2, column=1, pady=(10, 0))

        # Name Entry
        self.name_entry = CTkEntry(
            self,
            placeholder_text=self.translations["items"]["item_name"],
            width=290,
            height=50,
            border_color="#656565",
            fg_color="#202020",
            corner_radius=10,
            text_color="white",
            font=("Inter", 18, "bold"),
        )
        self.name_entry.grid(row=3, column=0, padx=(20, 10))

        # Inventory Frame
        self.inventory_frame = ChangeQuantityFrame(
            self,
            width=290,
            height=60,
            fg_color="#1C1C1C",
            corner_radius=10,
            border_width=2,
            border_color="#5D5D5D",
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
            border_color="#656565",
            fg_color="#202020",
            corner_radius=10,
            text_color="white",
            font=("Inter", 18, "bold"),
        )
        self.price_entry.grid(row=4, column=0, padx=(20, 10), pady=(10, 10))

        # Category Dropdown
        self.category_dropdown = CTkOptionMenu(
            self,
            values=[self.translations["items"]["drinks"], self.translations["items"]["snacks"]],
            width=290,  # Breite des Dropdown-Menüs
            height=50,
            fg_color="#202020",
            button_color="#202020",
            text_color="white",
            font=("Inter", 18, "bold"),
            button_hover_color="#333",
            dropdown_fg_color="#2B2B2B",  
            dropdown_text_color="white",  
            dropdown_hover_color="#575757",  
            dropdown_font=("Inter", 18, "bold"),  
        )
        self.category_dropdown.grid(
            row=4, column=1, padx=(20, 10), pady=(10, 10), sticky="w" 
        )

        # Add Barcode Button
        self.add_barcode_button = CTkButton(
            self,
            text=self.translations["items"]["add_barcode"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            fg_color="#2B2B2B",
            border_color="white",
            border_width=1,
            hover_color="#333333",
            command=self.show_barcode,
        )
        self.add_barcode_button.grid(row=5, column=0, padx=(20, 10), pady=(20, 10))

        # Add Item Button
        self.add_item_button = CTkButton(
            self,
            text=self.translations["items"]["add_item"],
            width=290,
            height=50,
            text_color="white",
            font=("Inter", 18, "bold"),
            fg_color="#129F07",
            hover_color="#13aF07",
            command=self.add_item,
        )
        self.add_item_button.grid(row=5, column=1, padx=(10, 20), pady=(20, 10))

    def upload_image_button_pressed(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            self.upload_image_tk = Image.open(file_path)
            self.file_path = file_path
            self.upload_image = self.upload_image_tk.resize(
                (100, 100), Image.Resampling.LANCZOS
            )
            self.upload_image = ImageTk.PhotoImage(self.upload_image)
            self.update_button.configure(image=self.upload_image)

    def confirm_barcode(self):
        self.barcode = self.barcode_frame.get()
        if self.barcode:
            self.barcode = str(self.barcode)
        self.barcode_frame.grab_release()
        self.barcode_frame.destroy()

    def show_barcode(self):
        self.barcode_frame = AddBarcodeFrame(self.parent, self.confirm_barcode)
        self.barcode_frame.grid(row=0, column=0, padx=20, pady=20)  # Ensure it is rendered fully
        self.barcode_frame.update_idletasks()  # Force the frame to update its layout
        self.barcode_frame.grab_set()

    def add_item(self):
        # Get data from entries and option menu
        name = self.name_entry.get()
        price = self.price_entry.get()
        category = self.category_dropdown.get()
        quantity = self.inventory_frame.get()
        barcode = self.barcode

        try:
            price = float(price)
        except:
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

        # Get image data
        image_data = None
        if hasattr(self, "file_path"):
            with open(self.file_path, "rb") as file:
                image_data = file.read()

        else:
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["items"]["error_adding_item"],
                text=self.translations["general"]["upload_image"],
            )
            self.parent.after(5000, self.message.destroy)

            return

        # Create a new Item instance
        new_item = Item(
            name=name,
            price=price,
            quantity=quantity,
            category=category,
            image=image_data,
            barcode=barcode
        )

        # Save the new item to the database
        new_item.create(self.session)
        
        self.back_button_function()