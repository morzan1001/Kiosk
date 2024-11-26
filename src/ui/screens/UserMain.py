from customtkinter import *
from typing import List
from tkinter import IntVar
from PIL import Image, ImageTk
from datetime import datetime
from src.logmgr import logger
from src.ui.components.Message import ShowMessage
from src.ui.components.ItemFrame import ItemFrame
from src.ui.components.QuantityFrame import QuantityFrame
from src.database import get_db, User, Item
from src.database.models.transaction import Transaction
from src.lock.gpio_manager import get_gpio_controller
from src.custom_email.email_manager import get_email_controller
from src.localization.translator import get_system_language, get_translations
from src.sounds.sound_manager import get_sound_controller
from src.mattermost.mattermost_manager import get_mattermost_controller

class UserMainPage(CTkFrame):
    def __init__(
        self, root, main_menu, user: User, items: List[Item], *args, **kwargs
    ):
        super().__init__(root, *args, **kwargs)

        self.barcode: str = ""
        self.items: List[Item] = items  # Store all items in memory
        self.displayed_items = (
            {}
        )  # Dictionary to track added items using item_id as key

        # Bind the event for handling barcode input (keypress events)
        root.bind("<Key>", self.on_barcode_scan)

        # Define the main frame
        self.grid(row=0, column=0, sticky="nsew")

        self.gpio_controller = get_gpio_controller()
        self.email_controller = get_email_controller()
        self.sound_controller = get_sound_controller()
        self.mattermost_controller = get_mattermost_controller()

        self.configure(width=800, height=480, fg_color="transparent")

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.root = root
        self.main_menu = main_menu
        self.user: User = user
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

        self.shopping_cart = []  # Store shopping_cart with items and quantity


        """
        This part of the code is commented out, as a specific decision can be made here. 
        On the one hand, all products can be displayed and selected. If you wish to do this, 
        the code should be commented in. However, if you only want the products that are 
        actually scanned to be displayed in the shopping cart, the code should be commented out. 
        the first is practical, for example, if you do not want to use a barcode scanner. 
        """
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
        #    self.shopping_cart.append((quantity, item))  # Store quantity and item details

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
            text=self.translations["user"]["welcome_user_message"].format(user_name=self.user.name),
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
            text=self.translations["user"]["credits_message"].format(user_credit=self.user.credit),
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
        item_id = item.id
        available_quantity = item.quantity

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
                # self.shopping_cart.append((quantity, item))  # Store quantity and item details

        else:
            # Add the item to the list as it has not been added yet
            quantity = IntVar()
            quantity.set(1)  # Initialize quantity to 1
            self.shopping_cart.append((quantity, item))  # Store quantity and item details
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
                item_price=item.price,
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

        for quantity, item in self.shopping_cart:
            total += int(quantity.get()) * float(item.price)
        self.total_price = total
        self.checkout_button.configure(text=self.translations["buttons"]["checkout_button"].format(total=self.total_price))

    def logout(self):
        self.destroy()
        self.gpio_controller.deactivate()
        self.main_menu(self.root).grid(row=0, column=0, sticky="nsew")

    def checkout(self):
        logger.debug("Starting checkout process")
        if self.total_price == 0:
            return

        user_credit = self.user.credit
        if self.total_price > float(user_credit):
            self._handle_insufficient_credit()
            return

        # First validate all items are available in requested quantities
        for quantity, item in self.shopping_cart:
            requested_quantity = int(quantity.get())
            if requested_quantity > item.quantity:
                self._handle_insufficient_quantity(item, requested_quantity)
                return

        # If validation passed, process the checkout
        try:
            self._process_checkout(user_credit)
            logger.debug("Checkout process completed successfully")
        except Exception as e:
            logger.error(f"Checkout failed: {str(e)}")
            self._handle_checkout_error()

    def _process_checkout(self, user_credit):
        current_datetime = datetime.now()
        logger.debug(f"Processing checkout at {current_datetime}")

        # Process all items in one loop
        for quantity, item in self.shopping_cart:
            requested_quantity = int(quantity.get())
            logger.debug(f"Processing item {item.id} with requested quantity {requested_quantity}")

            if requested_quantity <= 0:
                logger.debug(f"Skipping item {item.id} due to non-positive quantity")
                continue

            # Update item quantity
            item_instance = Item.get_by_id(self.session, item.id)
            if item_instance:
                new_quantity = item.quantity - requested_quantity
                logger.debug(f"Updating item {item.id} quantity to {new_quantity}")
                item_instance.update(self.session, quantity=new_quantity)

            # Create transaction
            new_transaction = Transaction(
                item_id=item.id,
                user_id=self.user.id,
                date=current_datetime,
                cost=str(item.price * requested_quantity),
                category=item.category
            )
            logger.debug(f"Creating transaction for item {item.id}")
            new_transaction.create(self.session)

            # Check stock levels
            self.check_product_stock_and_notify(item)

        # Update user credit
        new_credit = float(user_credit) - self.total_price
        user_instance = User.get_by_id(self.session, self.user.id)
        if user_instance:
            user_instance.update(self.session, credit=new_credit)
            self._check_low_balance(user_instance, new_credit)

        self._show_success_message()
        self.credits_label.configure(
            text=self.translations["user"]["credits_message"].format(user_credit=new_credit)
        )
        self.items = Item.read_all(self.session)
        
        if self.sound_controller:
            logger.debug("Playing positive sound on successful checkout")
            self.sound_controller.play_sound('positive')
        
        self.root.after(5000, self.logout)

    def _handle_insufficient_credit(self):
        if self.sound_controller:
            logger.debug("Playing negative sound due to insufficient credit")
            self.sound_controller.play_sound('negative')
        
        self.message = ShowMessage(
            self.root,
            image="unsuccessful",
            heading=self.translations["user"]["checkout_unsuccessful"],
            text=self.translations["user"]["insufficient_credit_message"],
        )
        self.root.after(5000, self.message.destroy)

    def _handle_checkout_error(self):
        self.message = ShowMessage(
            self.root,
            image="unsuccessful",
            heading=self.translations["user"]["checkout_unsuccessful"],
            text=self.translations["user"]["checkout_error_message"],
        )
        self.root.after(5000, self.message.destroy)

    def _handle_insufficient_quantity(self, item):
        if self.sound_controller:
            logger.debug("Playing negative sound due to insufficient product quantity")
            self.sound_controller.play_sound('negative')

        self.message = ShowMessage(
            self.root,
            image="unsuccessful",
            heading=self.translations["user"]["checkout_unsuccessful"],
            text=self.translations["items"]["item_quantity_message"].format(
                item_quantity=item.quantity, 
                name=item.name
            ),
        )
        self.root.after(5000, self.message.destroy)

    def _check_low_balance(self, user_instance, credit):
        if credit >= 3.0:
            return
            
        if user_instance.email:
            self.email_controller.notify_low_balance(
                recipient_email=user_instance.email,
                balance=credit,
                language=get_system_language()
            )
        if user_instance.mattermost_username:
            self.mattermost_controller.notify_low_balance(
                user=user_instance,
                balance=credit
            )

    def _show_success_message(self):
        self.message = ShowMessage(
            self.root,
            image="successful",
            heading=self.translations["user"]["checkout_successful"],
            text=self.translations["user"]["amount_debited"].format(total=self.total_price),
        )

    def on_barcode_scan(self, event):
        # Check if Enter key is pressed, which typically signals the end of a barcode scan
        if event.keysym == "Return":
            # Call the function to process the scanned barcode
            self.search_product(self.barcode)

            logger.debug(f"Scanned barcode: {self.barcode}")
            # Reset the barcode value after processing
            self.barcode = ""
        else:
            # Append the scanned character to the barcode string
            self.barcode += event.char

    def check_product_stock_and_notify(self, item: Item):
        logger.debug(f"Checking stock levels for item {item.id}")
        critical_stock_level = 3  # Define threshold
        
        if item.quantity < critical_stock_level:  # Assuming available_quantity is part of item
            admins: List[User] = User.get_admins(self.session)
            for admin in admins:
                if admin.email:
                    self.email_controller.notify_low_stock(
                        recipient_email=admin.email,
                        product_name=item.name,  
                        available_quantity=item.quantity,
                        language=get_system_language()
                    )
                if admin.mattermost_username:
                    self.mattermost_controller.notify_low_stock(
                        admin=admin.mattermost_username,
                        product_name=item.name,  
                        available_quantity=item.quantity
                    )

    def search_product(self, barcode_value: str):
        item: Item = Item.get_by_barcode(self.session, barcode_value)

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