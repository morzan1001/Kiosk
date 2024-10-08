from customtkinter import *
from tkinter import IntVar
from PIL import Image, ImageTk
from datetime import date
from logmgr import logger
from src.localization.translator import get_translations
from src.ui.components.Message import ShowMessage
from src.ui.components.ItemFrame import ItemFrame
from src.ui.components.QuantityFrame import QuantityFrame
from src.database import get_db, User, Item
from src.database.models.transaction import Transaction
from src.lock.gpio_manager import get_gpio_controller

class UserMainPage(CTkFrame):
    def __init__(
        self, root, main_menu, user_id, user_name, user_credit, items, *args, **kwargs
    ):
        super().__init__(root, *args, **kwargs)

        self.barcode = ""
        self.items = items  # Store all items in memory
        self.displayed_items = (
            {}
        )  # Dictionary to track added items using item_id as key

        # Bind the event for handling barcode input (keypress events)
        root.bind("<Key>", self.on_barcode_scan)

        # Define the main frame
        self.grid(row=0, column=0, sticky="nsew")

        self.gpio_controller = get_gpio_controller()

        self.configure(width=800, height=480, fg_color="transparent")

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.root = root
        self.main_menu = main_menu
        self.user_id = user_id
        self.user_name = user_name
        self.user_credit = user_credit
        self.translations = get_translations()

        self.total_price = 0.0  # Initialize total price

        self.session = get_db()

        user_image = ImageTk.PhotoImage(Image.open("src/images/user.png"))
        credit_image = ImageTk.PhotoImage(Image.open("src/images/credit.png"))

        # Item list
        self.item_frame = CTkScrollableFrame(
            self, fg_color="white", width=580, height=260
        )
        self.item_frame.grid(row=1, rowspan=2, column=0, columnspan=4)
        self.item_frame.grid_columnconfigure(0, weight=1)

        #for i in range(len(self.items)):
        #    self.item_frame.grid_rowconfigure(i, weight=1)

        self.quantities = []  # Store quantities of items

        # Add frames for items
        #for indx, item in enumerate(self.items):
        #    sub_frame = CTkFrame(
        #        self.item_frame, fg_color="white", width=580, height=60
        #    )
        #    sub_frame.grid(row=indx, column=0, padx=10, pady=10, sticky="nsew")

        #    # Configure grid for sub_frame
        #    sub_frame.grid_rowconfigure(0, weight=1)
        #    sub_frame.grid_columnconfigure(0, weight=1)
        #    sub_frame.grid_columnconfigure(1, weight=1)

        #    # Create an IntVar for the quantity
        #    quantity = IntVar()
        #    quantity.set(0)  # Initialize quantity to 0
        #    self.quantities.append((quantity, item))  # Store quantity and item details

        #    # Add widgets to the sub_frame
        #    ItemFrame(sub_frame, data=item, fg_color="white").grid(
        #        row=0, column=0, sticky="w"
        #    )

        #    QuantityFrame(
        #        sub_frame,
        #        data=quantity,
        #        update_total_price=self.update_total_price,
        #        item_price=item[3],
        #        border_width=1,
        #        fg_color="white",
        #        border_color="#D3D3D3",
        #        corner_radius=15,
        #    ).grid(row=0, column=1, sticky="e", ipadx=10, ipady=5)

        # Welcome label
        welcome_label = CTkButton(
            self,
            image=user_image,
            text=self.translations["user"]["welcome_user_message"].format(user_name=self.user_name),
            font=("Arial", 18, "bold"),
            fg_color="white",
            hover_color="white",
            text_color="black",
            width=290,
            height=60,
        )
        welcome_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="e")

        # Credits label
        self.credits_label = CTkButton(
            self,
            image=credit_image,
            text=self.translations["user"]["credits_message"].format(user_credit=self.user_credit),
            font=("Arial", 18, "bold"),
            fg_color="white",
            hover_color="white",
            text_color="black",
            width=290,
            height=60,
        )
        self.credits_label.grid(
            row=0, column=2, columnspan=2, pady=10, padx=10, sticky="w"
        )

        # Cancel and checkout buttons
        cancel_button = CTkButton(
            self,
            text=self.translations["buttons"]["cancel_button"],
            width=280,
            height=50,
            font=("Arial", 16, "bold"),
            corner_radius=10,
            border_color="white",
            border_width=2,
            fg_color="transparent",
            hover_color="#333",
            command=self.logout,
        )
        cancel_button.grid(row=3, column=0, columnspan=2, pady=20, padx=20, sticky="e")

        self.checkout_button = CTkButton(
            self,
            text=self.translations["buttons"]["checkout_button"].format(total=0),
            width=280,
            height=50,
            font=("Arial", 16, "bold"),
            corner_radius=10,
            fg_color="#129F07",
            hover_color="#15aF07",
            command=self.checkout,
        )
        self.checkout_button.grid(
            row=3, column=2, columnspan=2, pady=20, padx=20, sticky="w"
        )

    def add_item_to_list(self, item):
        """
        Adds the scanned item to the UI list if it's not already added.
        Updates the quantity if the item is already added.
        """
        item_id = item[0]  # Assuming the first element in the tuple is the item_id
        available_quantity = item[-2]

        if item_id in self.displayed_items:
            # Item is already displayed, so increment the quantity
            quantity_var, _ = self.displayed_items[item_id]
            current_quantity = quantity_var.get()
            # Ensure that the new quantity does not exceed the available stock
            if current_quantity + 1 > available_quantity:
                # Show a message indicating that the user cannot add more items than available
                self.message = ShowMessage(
                    self.root,
                    image="unsuccessful",
                    heading=self.translations["items"]["quantity_limit_reached"],
                    text=self.translations["items"]["item_quantity_message"].format(item_quantity=available_quantity, name=item[2]),
                )
                self.root.after(5000, self.message.destroy)
                return
            else:
                # Increment the quantity in the UI if there's enough stock
                quantity_var.set(current_quantity + 1)
                self.update_total_price()
                # self.quantities.append((quantity, item))  # Store quantity and item details

        else:
            # Add the item to the list as it has not been added yet
            quantity = IntVar()
            quantity.set(1)  # Initialize quantity to 1
            self.quantities.append((quantity, item))  # Store quantity and item details
            self.update_total_price()

            indx = len(self.displayed_items)  # New row index
            self.item_frame.grid_rowconfigure(indx, weight=1)
            sub_frame = CTkFrame(
                self.item_frame, fg_color="white", width=580, height=60
            )
            sub_frame.grid(row=indx, column=0, padx=10, pady=10, sticky="nsew")

            # Configure grid for sub_frame
            sub_frame.grid_rowconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(1, weight=1)

            # Add widgets to the sub_frame
            ItemFrame(sub_frame, data=item, fg_color="white").grid(
                row=0, column=0, sticky="w"
            )

            quantity_frame = QuantityFrame(
                sub_frame,
                data=quantity,
                update_total_price=self.update_total_price,
                item_price=item[3],
                border_width=1,
                fg_color="white",
                border_color="#D3D3D3",
                corner_radius=15,
            )
            quantity_frame.grid(row=0, column=1, sticky="e", ipadx=10, ipady=5)

            # Store the quantity widget and item details in displayed_items
            self.displayed_items[item_id] = (quantity, item)

    def update_total_price(self):
        total = 0.0

        for quantity, item in self.quantities:
            total += int(quantity.get()) * float(item[3])
        self.total_price = total
        self.checkout_button.configure(text=self.translations["buttons"]["checkout_button"].format(total=self.total_price))

    def logout(self):
        self.destroy()
        self.gpio_controller.deactivate()
        self.main_menu(self.root).grid(row=0, column=0, sticky="nsew")

    def checkout(self):
        for quantity, item in self.quantities:
            requested_quantity = int(quantity.get())
            item_id, _, name, _, item_quantity, _ = item

            if requested_quantity > item_quantity:
                self.message = ShowMessage(
                    self.root,
                    image="unsuccessful",
                    heading=self.translations["user"]["checkout_unsuccessful"],
                    text=self.translations["items"]["item_quantity_message"].format(item_quantity=item_quantity, name=name),
                )
                self.root.after(5000, self.message.destroy)
                return
            
        if self.total_price == 0:
            return
        elif self.total_price > float(self.user_credit):
            self.message = ShowMessage(
                self.root,
                image="unsuccessful",
                heading=self.translations["user"]["checkout_unsuccessful"],
                text=self.translations["user"]["insufficient_credit_message"],
            )
            self.root.after(5000, self.message.destroy)
        else:
            current_date = date.today()
            formatted_date = current_date.strftime("%Y-%m-%d")
            for quantity, item in self.quantities:
                requested_quantity = int(quantity.get())

                if requested_quantity > 0:
                    item_id, _, name, price, item_quantity, category = item
                    new_quantity = item_quantity - requested_quantity

                    # Load the item using the class method get_by_id
                    item_instance = Item.get_by_id(self.session, item_id)
                    if item_instance:
                        # Update the item
                        item_instance.update(self.session, quantity=new_quantity)

                    # Create and save a new transaction
                    new_transaction = Transaction(
                        user_id=self.user_id, 
                        date=formatted_date, 
                        cost=str(price * requested_quantity), 
                        category=category
                    )
                    new_transaction.create(self.session)

            # Update the user's credit   
            credit = float(self.user_credit) - self.total_price
            user_instance = User.get_by_id(self.session, self.user_id)
            if user_instance:
                user_instance.update(self.session, credit=credit)

            # Show success message
            self.message = ShowMessage(
                self.root,
                image="successful",
                heading=self.translations["user"]["checkout_successful"],
                text=self.translations["user"]["amount_debited"].format(total=self.total_price),
            )
            self.user_credit = self.user_credit - self.total_price
            self.credits_label.configure(text=self.translations["user"]["credits_message"].format(user_credit=self.user_credit))
            self.items = Item.read_all(self.session)
            self.root.after(5000, self.logout)


    def on_barcode_scan(self, event):
        # Check if Enter key is pressed, which typically signals the end of a barcode scan
        if event.keysym == "Return":
            # Call the function to process the scanned barcode
            self.process_barcode(self.barcode)

            logger.debug(f"Scanned barcode: {self.barcode}")
            # Reset the barcode value after processing
            self.barcode = ""
        else:
            # Append the scanned character to the barcode string
            self.barcode += event.char

    def process_barcode(self, barcode_value):
        # Function to handle the barcode value
        self.search_product(barcode_value)

    def search_product(self, barcode_value):
        item = Item.get_by_barcode(self.session, barcode_value)

        if item:
            self.add_item_to_list(item)
        else:
            self.message = ShowMessage(
                self.root,
                image="unsuccessful",
                heading=self.translations["items"]["item_not_found"],
                text=self.translations["items"]["scanned_item_not_found"],
            )
            self.root.after(5000, self.message.destroy)