import logging
import math
from datetime import datetime, timedelta

from customtkinter import CTkButton, CTkCanvas, CTkEntry, CTkFrame, CTkLabel, CTkOptionMenu

from src.database import Transaction, User, get_db
from src.localization.translator import get_translations
from src.ui.components.confirmation import DeleteConfirmation
from src.ui.components.credit_frame import CreditFrame
from src.ui.components.heading_frame import HeadingFrame
from src.ui.components.message import ShowMessage
from src.ui.components.scan_card import ScanCardFrame

# Initialize the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class UpdateUserFrame(CTkFrame):
    def __init__(self, parent, back_button_function, user_id: int, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        logger.debug("Initializing UpdateUserFrame with user_id=%s", user_id)

        self.chartColors = ["#0FD600", "#EA68FF", "#E8AF1A", "#FF6B6B", "#4ECDC4"]

        self.parent = parent
        self.back_button_function = back_button_function
        self.user_id: int = user_id
        self.translations = get_translations()
        self.nfcid: str = ""

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        # Configure the grid for the frame
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        # Heading Frame
        heading_frame = HeadingFrame(
            self,
            heading_text=self.translations["admin"]["update_user"],
            back_button_function=back_button_function,
            delete_button_function=self.delete_user,
            width=600,
            fg_color="transparent",
        )
        heading_frame.grid(row=0, column=0, columnspan=2, padx=90, sticky="new")

        # Credits label
        credits_label = CTkLabel(
            self,
            text=self.translations["user"]["credits_label"],
            width=290,
            anchor="w",
            font=("Arial", 18, "bold"),
        )
        credits_label.grid(row=1, column=1, pady=(10, 0), sticky="s")

        # Name entry
        self.name_entry = CTkEntry(
            self,
            placeholder_text=self.translations["user"]["enter_name"],
            width=290,
            height=50,
            corner_radius=10,
            font=("Inter", 18, "bold"),
        )
        self.name_entry.grid(row=2, column=0, padx=(20, 10), sticky="e")

        # Credits frame
        self.credits_frame = CreditFrame(
            self,
            width=290,
            height=60,
            corner_radius=10,
            border_width=2,
        )
        self.credits_frame.grid(row=2, column=1, padx=(10, 20), pady=(10, 10), sticky="w")

        # Type dropdown
        self.user_type_menu = CTkOptionMenu(
            self,
            values=[
                self.translations["user"]["user"],
                self.translations["admin"]["admin"],
            ],
            width=620,
            height=50,
            font=("Inter", 18, "bold"),
            dropdown_font=("Inter", 18, "bold"),
        )
        self.user_type_menu.grid(
            row=3, column=0, columnspan=2, pady=(10, 10), padx=(20, 20), sticky="n"
        )

        # Graph frame - update to match dropdown positioning
        self.graph_frame = CTkFrame(self, width=620, height=120, corner_radius=10)
        self.graph_frame.grid(
            row=4, column=0, columnspan=2, padx=(20, 20), pady=(10, 10), sticky="n"
        )
        self.graph_frame.grid_propagate(False)

        # Update NFCID button
        self.update_nfcid_button = CTkButton(
            self,
            text=self.translations["nfc"]["update_nfcid"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.show_scan_card,
        )
        self.update_nfcid_button.grid(
            row=5, column=0, padx=(20, 10), pady=(20, 10), sticky="e"
        )  # Added sticky="e"

        # Update user button
        self.update_user_button = CTkButton(
            self,
            text=self.translations["admin"]["update_user"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.update_user,
        )
        self.update_user_button.grid(
            row=5, column=1, padx=(10, 20), pady=(20, 10), sticky="w"
        )  # Added sticky="w"

        self.initialize_user()

    def draw_pie_chart(self, category_percentages):
        """Draw a pie chart using CTkCanvas"""
        # Clear the graph frame
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        if not category_percentages:
            # Show empty state
            empty_label = CTkLabel(
                self.graph_frame,
                text=self.translations.get("user", {}).get("no_transactions", "No transactions"),
                text_color="#888888",
                font=("Arial", 14),
            )
            empty_label.place(relx=0.5, rely=0.5, anchor="center")
            return

        # Create main container - centered
        container = CTkFrame(self.graph_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Create canvas for pie chart
        canvas = CTkCanvas(container, width=100, height=100, bg="#1C1C1C", highlightthickness=0)
        canvas.pack(side="left", padx=(0, 20))

        # Pie chart parameters
        center_x, center_y = 50, 50
        radius = 40
        start_angle = 0

        # Draw pie slices
        for i, (category, percentage) in enumerate(category_percentages.items()):
            # Calculate the angle for this slice
            extent = (percentage / 100) * 360

            # Get color
            color = self.chartColors[i % len(self.chartColors)]

            # Draw the arc (pie slice)
            canvas.create_arc(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                start=start_angle,
                extent=extent,
                fill=color,
                outline="#1C1C1C",
                width=2,
            )

            # Only draw percentage text if the slice is large enough
            if extent > 15:  # Only show text for slices larger than 15 degrees
                mid_angle = start_angle + extent / 2
                text_radius = radius * 0.7
                text_x = center_x + text_radius * math.cos(math.radians(mid_angle))
                text_y = center_y - text_radius * math.sin(math.radians(mid_angle))

                canvas.create_text(
                    text_x,
                    text_y,
                    text=f"{int(percentage)}%",
                    fill="white",
                    font=("Arial", 9, "bold"),
                )

            start_angle += extent

        # Legend container
        legend_frame = CTkFrame(container, fg_color="transparent")
        legend_frame.pack(side="left", fill="y")

        # Legend heading
        heading_label = CTkLabel(
            legend_frame,
            text=self.translations["user"]["last_month_purchase"],
            text_color="white",
            font=("Arial", 11, "bold"),
            anchor="w",
        )
        heading_label.pack(anchor="w", pady=(0, 5))

        # Legend items
        for i, (category, percentage) in enumerate(category_percentages.items()):
            if i >= 5:  # Limit to 5 items
                break

            item_frame = CTkFrame(legend_frame, fg_color="transparent", height=20)
            item_frame.pack(fill="x", pady=1)
            item_frame.pack_propagate(False)

            color = self.chartColors[i % len(self.chartColors)]

            # Color indicator
            color_box = CTkFrame(item_frame, width=10, height=10, fg_color=color, corner_radius=5)
            color_box.pack(side="left", padx=(0, 5), pady=(5, 0))

            # Category label
            category_label = CTkLabel(
                item_frame,
                text=f"{category}: {int(percentage)}%",
                text_color="white",
                font=("Arial", 10),
                anchor="w",
            )
            category_label.pack(side="left", fill="x", expand=True, pady=(5, 0))

    def initialize_user(self):
        logger.debug("Calling initialize_user for user_id=%s", self.user_id)
        user = User.get_by_id(self.session, self.user_id)
        if user:
            name = user.name
            self.nfcid = user.nfcid
            credit = user.credit
            user_type = user.type

            logger.debug(
                "User data loaded: name=%s, nfcid=%s, credit=%s, type=%s",
                name,
                self.nfcid,
                credit,
                user_type,
            )

            self.name_entry.insert(0, name)
            self.credits_frame.set_entry_text(credit)
            self.user_type_menu.set(user_type)

            transactions = Transaction.read_all_for_user(self.session, self.user_id)
            logger.debug("Number of transactions found: %d", len(transactions))

            last_month_transactions = self.get_transactions_last_month(transactions)
            logger.debug(
                "Number of transactions in the last month: %d",
                len(last_month_transactions),
            )

            category_percentages = self.calculate_category_percentage(last_month_transactions)
            logger.debug("Calculated category percentages: %s", category_percentages)

            # Draw the pie chart
            self.draw_pie_chart(category_percentages)

        else:
            logger.debug("No user found with user_id=%s", self.user_id)

    def get_transactions_last_month(self, transactions):
        logger.debug("Filtering transactions from the last month")
        current_date = datetime.now()
        start_date = current_date - timedelta(days=30)

        filtered_transactions = []
        for transaction in transactions:
            date_transaction = transaction.date
            if start_date <= date_transaction <= current_date:
                filtered_transactions.append(transaction)

        logger.debug("Filtered transactions count: %d", len(filtered_transactions))
        return filtered_transactions

    def calculate_category_percentage(self, transactions):
        logger.debug("Calculating category percentages")
        category_totals = {}
        total_amount = sum(float(transaction.cost) for transaction in transactions)

        logger.debug("Total transaction amount: %f", total_amount)

        for transaction in transactions:
            category = transaction.category
            amount = float(transaction.cost)

            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

            logger.debug("Updated category '%s' with amount %f", category, amount)

        if total_amount > 0:
            category_percentages = {
                category: (amount / total_amount) * 100
                for category, amount in category_totals.items()
            }
        else:
            category_percentages = {}

        logger.debug("Calculated category percentages: %s", category_percentages)
        return category_percentages

    def show_scan_card(self):
        logger.debug("Displaying ScanCardFrame to update NFCID")
        self.nfcid = ""
        self.scan_card_frame = ScanCardFrame(
            parent=self.parent,
            heading_text=self.translations["nfc"]["update_nfcid"],
            set_nfcid_id=self.set_nfcid_id,
            back_button_function=self.remove_scan_card,
        )
        self.scan_card_frame.grid(row=0, column=0, sticky="nsew")

    def remove_scan_card(self):
        logger.debug("Removing ScanCardFrame")
        self.scan_card_frame.destroy()

    def update_user(self):
        logger.debug("Starting update_user")
        name = self.name_entry.get().strip()
        user_credits = self.credits_frame.get()
        user_type = self.user_type_menu.get()
        nfcid = self.nfcid.strip()

        logger.debug(
            "Input data: name='%s', nfcid='%s', user_credits='%s', type='%s'",
            name,
            nfcid,
            user_credits,
            user_type,
        )

        if not (name and nfcid):
            logger.debug("Name or NFCID is missing")
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["admin"]["error_updating_user"],
                text=self.translations["admin"]["missing_nfcid_name"],
            )
            self.parent.after(5000, self.message.destroy)
            return

        existing_user = User.get_by_nfcid(self.session, nfcid)
        logger.debug("Checking existing_user with nfcid='%s': %s", nfcid, existing_user)

        if existing_user and existing_user.id != self.user_id:
            logger.debug("NFCID '%s' is already used by user_id '%s'", nfcid, existing_user.id)
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["admin"]["error_updating_user"],
                text=self.translations["nfc"]["card_already_used"],
            )
            self.parent.after(5000, self.message.destroy)
        else:
            user_instance = User.get_by_id(self.session, self.user_id)
            logger.debug("Updating user: %s", user_instance)
            if user_instance:
                try:
                    user_instance.update(
                        self.session,
                        nfcid=nfcid,
                        name=name,
                        type=user_type,
                        credit=user_credits,
                    )
                    logger.debug("User updated successfully")
                except Exception as e:
                    logger.exception("Error updating user")
                    self.message = ShowMessage(
                        self.parent,
                        image="unsuccessful",
                        heading=self.translations["admin"]["error_updating_user"],
                        text=str(e),
                    )
                    self.parent.after(5000, self.message.destroy)
                    return
            else:
                logger.debug("User with user_id=%s not found", self.user_id)
            self.back_button_function()

    def set_nfcid_id(self, new_nfcid):
        logger.debug("Setting new NFCID: %s", new_nfcid)
        self.nfcid = new_nfcid

    def confirm_delete(self):
        logger.debug("Confirming deletion of user with user_id=%s", self.user_id)
        user_instance = User.get_by_id(self.session, self.user_id)
        if user_instance:
            user_instance.delete(self.session)
            logger.debug("User deleted")
        else:
            logger.debug("User to delete not found")
        self.back_button_function()

    def delete_user(self):
        logger.debug("Delete confirmation for user with user_id=%s", self.user_id)
        DeleteConfirmation(self.parent, self.confirm_delete, self.translations["user"]["user"])
