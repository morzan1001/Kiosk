"""User purchase flow screen.

This screen is shown after a user logs in (e.g. via NFC). It manages the
shopping cart UI, checkout transaction, and optional notifications.
"""

from datetime import datetime
from tkinter import IntVar
from typing import List

import sqlalchemy.exc
from customtkinter import CTkButton, CTkFrame, CTkImage, CTkScrollableFrame
from PIL import Image

from src.database import Item, User, get_db
from src.database.models.transaction import Transaction
from src.localization.translator import get_system_language, get_translations
from src.lock.gpio_manager import get_gpio_controller
from src.logmgr import logger
from src.messaging.email import get_email_controller
from src.messaging.mattermost import get_mattermost_controller
from src.sounds.sound_manager import get_sound_controller
from src.ui.components.item_frame import ItemFrame
from src.ui.components.Message import ShowMessage
from src.ui.components.quantity_frame import QuantityFrame
from src.ui.navigation import clear_root
from src.utils.paths import get_image_path


class UserMainPage(CTkFrame):
    """Main user screen for selecting items and checking out."""
    def __init__(self, root, main_menu, user: User, items: List[Item], *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.barcode: str = ""
        self.items: List[Item] = items
        self.displayed_items = {}

        root.bind("<Key>", self.on_barcode_scan)

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

        self.total_price = 0.0

        self.session = get_db()

        user_img = Image.open(get_image_path("user.png"))
        user_image = CTkImage(light_image=user_img, dark_image=user_img)

        credit_img = Image.open(get_image_path("credit.png"))
        credit_image = CTkImage(light_image=credit_img, dark_image=credit_img)

        self.item_frame = CTkScrollableFrame(self, fg_color="white", width=760, height=260)
        self.item_frame.grid(
            row=1, rowspan=2, column=0, columnspan=4, padx=20, pady=10, sticky="nsew"
        )
        self.item_frame.grid_columnconfigure(0, weight=1)

        self.shopping_cart = []

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
        welcome_label.grid(row=0, column=0, columnspan=2, pady=10, padx=(20, 10), sticky="ew")

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
        self.credits_label.grid(row=0, column=2, columnspan=2, pady=10, padx=(10, 20), sticky="ew")

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
        cancel_button.grid(row=3, column=0, columnspan=2, pady=20, padx=(20, 10), sticky="ew")

        self.checkout_button = CTkButton(
            self,
            text=self.translations["buttons"]["checkout_button"].format(total=0),
            width=280,
            height=50,
            font=("Arial", 16, "bold"),
            corner_radius=10,
            command=self.checkout,
        )
        self.checkout_button.grid(
            row=3, column=2, columnspan=2, pady=20, padx=(10, 20), sticky="ew"
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
                    text=self.translations["items"]["item_quantity_message"].format(
                        item_quantity=available_quantity, name=item.name
                    ),
                )
                self.root.after(5000, self.message.destroy)
            else:
                # Increment the quantity in the UI if there's enough stock
                quantity_var.set(current_quantity + 1)
                self.update_total_price()

        else:
            # Add the item to the list as it has not been added yet
            quantity = IntVar()
            quantity.set(1)  # Initialize quantity to 1
            self.shopping_cart.append((quantity, item))  # Store quantity and item details
            self.update_total_price()

            indx = len(self.displayed_items)  # New row index
            self.item_frame.grid_rowconfigure(indx, weight=1)
            sub_frame = CTkFrame(self.item_frame, fg_color="white", width=740, height=60)
            sub_frame.grid(row=indx, column=0, padx=10, pady=10, sticky="nsew")

            # Configure grid for sub_frame
            sub_frame.grid_rowconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(1, weight=1)

            # Add widgets to the sub_frame
            ItemFrame(sub_frame, data=item, fg_color="white").grid(row=0, column=0, sticky="w")

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
        self.checkout_button.configure(
            text=self.translations["buttons"]["checkout_button"].format(total=self.total_price)
        )

    def logout(self):
        clear_root(self.root)
        self.gpio_controller.deactivate()
        self.main_menu(self.root).grid(row=0, column=0, sticky="nsew")

    def checkout(self):
        """Validate cart and execute checkout as one DB transaction."""
        logger.debug("Starting checkout process")
        if self.total_price == 0:
            logger.debug("No items in the shopping cart")
            return

        user_credit = self.user.credit
        if self.total_price > float(user_credit):
            logger.debug(
                (
                    f"Insufficient credit for checkout. Total price: {self.total_price}, "
                    f"User credit: {user_credit}"
                )
            )
            self._handle_insufficient_credit()
            return

        # First validate all items are available in requested quantities
        for quantity, item in self.shopping_cart:
            requested_quantity = int(quantity.get())
            if requested_quantity > item.quantity:
                logger.debug(
                    (
                        f"Insufficient quantity for item {item.id}. Requested: "
                        f"{requested_quantity}, Available: {item.quantity}"
                    )
                )
                self._handle_insufficient_quantity(item)
                return

        # If validation passed, process the checkout
        try:
            self._process_checkout(user_credit)
            logger.debug("Checkout process completed successfully")
        except (ValueError, sqlalchemy.exc.SQLAlchemyError):
            logger.exception("Checkout failed")
            self._handle_checkout_error()

    def _process_checkout(self, user_credit):
        """Perform the checkout transaction (row locks, updates, commit/rollback)."""
        current_datetime = datetime.now()
        logger.debug("Processing checkout at %s", current_datetime)

        try:
            # Process all items in one loop
            for quantity, item_in_cart in self.shopping_cart:
                requested_quantity = int(quantity.get())
                logger.debug(
                    (
                        f"Processing item {item_in_cart.id} with requested quantity "
                        f"{requested_quantity}"
                    )
                )

                if requested_quantity <= 0:
                    logger.debug(
                        "Skipping item %s due to non-positive quantity",
                        item_in_cart.id,
                    )
                    continue

                # Re-fetch item with row lock to prevent race conditions
                locked_item = (
                    self.session.query(Item).filter_by(id=item_in_cart.id).with_for_update().first()
                )

                if not locked_item:
                    raise ValueError(f"Item {item_in_cart.name} not found")

                # Validate quantity against the locked row
                if locked_item.quantity < requested_quantity:
                    raise ValueError(
                        f"Insufficient stock for {locked_item.name}. "
                        f"Available: {locked_item.quantity}, Requested: {requested_quantity}"
                    )

                # Update item quantity - NO COMMIT YET
                new_quantity = locked_item.quantity - requested_quantity
                logger.debug(
                    "Updating item %s quantity to %s",
                    locked_item.id,
                    new_quantity,
                )
                locked_item.update(self.session, commit=False, quantity=new_quantity)

                # Create transaction - NO COMMIT YET
                new_transaction = Transaction(
                    item_id=locked_item.id,
                    user_id=self.user.id,
                    date=current_datetime,
                    cost=str(locked_item.price * requested_quantity),
                    category=locked_item.category,
                )
                logger.debug("Creating transaction for item %s", locked_item.id)
                new_transaction.create(self.session, commit=False)

            # Update user credit - NO COMMIT YET
            # Lock user row to prevent race conditions on credit
            locked_user = (
                self.session.query(User).filter_by(id=self.user.id).with_for_update().first()
            )

            if not locked_user:
                raise ValueError("User not found")

            if locked_user.credit < self.total_price:
                raise ValueError("Insufficient credit")

            new_credit = float(locked_user.credit) - self.total_price
            locked_user.update(self.session, commit=False, credit=new_credit)

            # COMMIT EVERYTHING AT ONCE
            self.session.commit()
            logger.info("Checkout transaction committed successfully")

            # Post-commit actions (Notifications)
            if locked_user:
                self._check_low_balance(locked_user, new_credit)

            for quantity, item_in_cart in self.shopping_cart:
                # Re-fetch to get the updated quantity for notification check
                updated_item = Item.get_by_id(self.session, item_in_cart.id)
                if updated_item:
                    self.check_product_stock_and_notify(updated_item)

            self._show_success_message()
            self.credits_label.configure(
                text=self.translations["user"]["credits_message"].format(user_credit=new_credit)
            )
            self.items = Item.read_all(self.session)

            if self.sound_controller:
                logger.debug("Playing positive sound on successful checkout")
                self.sound_controller.play_sound("positive")

            self.root.after(5000, self.logout)

        except (ValueError, sqlalchemy.exc.SQLAlchemyError):
            self.session.rollback()
            logger.exception("Checkout failed, rolled back")
            raise

    def _handle_insufficient_credit(self):
        if self.sound_controller:
            logger.debug("Playing negative sound due to insufficient credit")
            self.sound_controller.play_sound("negative")

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
            self.sound_controller.play_sound("negative")

        self.message = ShowMessage(
            self.root,
            image="unsuccessful",
            heading=self.translations["user"]["checkout_unsuccessful"],
            text=self.translations["items"]["item_quantity_message"].format(
                item_quantity=item.quantity, name=item.name
            ),
        )
        logger.debug("Showing insufficient quantity message for item %s", item.id)
        self.root.after(5000, self.message.destroy)

    def _check_low_balance(self, user_instance, credit):
        if credit >= 3.0:
            return

        if user_instance.email:
            self.email_controller.notify_low_balance(
                recipient=user_instance.email,
                balance=credit,
                language=get_system_language(),
            )
        if user_instance.mattermost_username:
            self.mattermost_controller.notify_low_balance(recipient=user_instance, balance=credit)

    def _show_success_message(self):
        self.message = ShowMessage(
            self.root,
            image="successful",
            heading=self.translations["user"]["checkout_successful"],
            text=self.translations["user"]["amount_debited"].format(total=self.total_price),
        )

    def on_barcode_scan(self, event):
        """Handle keyboard-emulated barcode scanner input."""
        # Check if Enter key is pressed, which typically signals the end of a barcode scan
        if event.keysym == "Return":
            # Call the function to process the scanned barcode
            self.search_product(self.barcode)

            logger.debug("Scanned barcode: %s", self.barcode)
            # Reset the barcode value after processing
            self.barcode = ""
        else:
            # Append the scanned character to the barcode string
            self.barcode += event.char

    def check_product_stock_and_notify(self, item: Item):
        """Notify admins when stock is below a critical threshold."""
        logger.debug("Checking stock levels for item %s", item.id)
        critical_stock_level = 3  # Define threshold

        if item.quantity < critical_stock_level:  # Assuming available_quantity is part of item
            admins: List[User] = User.get_admins(self.session)
            for admin in admins:
                if admin.email:
                    self.email_controller.notify_low_stock(
                        recipient=admin.email,
                        product_name=item.name,
                        available_quantity=item.quantity,
                        language=get_system_language(),
                    )
                if admin.mattermost_username:
                    self.mattermost_controller.notify_low_stock(
                        recipient=admin,
                        product_name=item.name,
                        available_quantity=item.quantity,
                    )

    def search_product(self, barcode_value: str):
        """Lookup an item by barcode and add it to the cart if found."""
        item: Item = Item.get_by_barcode(self.session, barcode_value)

        if item:
            self.add_item_to_list(item)
            logger.debug(
                "Item with barcode %s found. %s added to shopping cart",
                barcode_value,
                item.name,
            )
        else:
            logger.debug("Item with barcode %s not found", barcode_value)
            self.message = ShowMessage(
                self.root,
                image="unsuccessful",
                heading=self.translations["items"]["item_not_found"],
                text=self.translations["items"]["scanned_item_not_found"],
            )
            self.root.after(5000, self.message.destroy)
