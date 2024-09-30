import logging
import customtkinter
from customtkinter import *
from src.localization.translator import get_translations
from src.ui.components.ctkchart import CTkPieChart
from src.ui.components.HeadingFrame import HeadingFrame
from src.database import get_db, User, Transaction
from src.ui.components.ScanCard import ScanCardFrame
from src.ui.components.Confirmation import DeleteConfirmation
from src.ui.components.CreditFrame import CreditFrame
from src.ui.components.Message import ShowMessage
from datetime import datetime, timedelta

# Initialize the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class UpdateUserFrame(CTkFrame):
    def __init__(self, parent, back_button_function, user_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        logger.debug("Initializing UpdateUserFrame with user_id=%s", user_id)

        self.chartColors = {"#0FD600": "white", "#EA68FF": "white", "#E8AF1A": "white"}

        self.parent = parent
        self.back_button_function = back_button_function
        self.user_id = user_id
        self.translations = get_translations()
        self.nfcid = ""

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        # Configure the grid for the frame
        self.grid_columnconfigure((0, 1), weight=1)
        # Set graph row (row 4) weight to 0 to prevent it from stretching and squashing other elements
        self.grid_rowconfigure(0, weight=1)  # Heading
        self.grid_rowconfigure(1, weight=1)  # Credits Label
        self.grid_rowconfigure(2, weight=1)  # Name Entry and Credits Frame
        self.grid_rowconfigure(3, weight=1)  # User Type
        self.grid_rowconfigure(4, weight=0)  # Graph Frame (reduced weight)
        self.grid_rowconfigure(5, weight=1)  # Update NFCID and Update User Buttons
        self.grid_rowconfigure(6, weight=1)  # Spacer

        heading_frame = HeadingFrame(
            self,
            heading_text=self.translations["admin"]["update_user"],
            back_button_function=back_button_function,
            delete_button_function=self.delete_user
        )
        heading_frame.grid(row=0, column=0, columnspan=2, padx=40, pady=(10, 10))

        credits_label = CTkLabel(
            self,
            text=self.translations["user"]["credits_label"],
            width=290,
            anchor="w",
            text_color="white",
            font=("Inter", 16, "bold"),
        )
        credits_label.grid(row=1, column=1, sticky="s", pady=(5, 5))

        self.name_entry = CTkEntry(
            self,
            placeholder_text=self.translations["user"]["enter_name"],
            width=290,
            height=40,
            border_color="#656565",
            fg_color="#202020",
            corner_radius=10,
            text_color="white",
            font=("Inter", 16, "bold"),
        )
        self.name_entry.grid(row=2, column=0, padx=(20, 10), pady=(5, 5))

        self.credits_frame = CreditFrame(
            self,
            width=290,
            height=40,
            fg_color="#1C1C1C",
            corner_radius=10,
            border_width=2,
            border_color="#5D5D5D",
        )
        self.credits_frame.grid(row=2, column=1, padx=(10, 20), pady=(5, 5), sticky="w")

        self.user_type = CTkOptionMenu(
            self,
            values=[self.translations["user"]["user"], self.translations["admin"]["admin"]],
            width=600,
            height=40,
            fg_color="#202020",
            button_color="#202020",
            text_color="white",
            font=("Inter", 16, "bold"),
            button_hover_color="#333",
            dropdown_fg_color="#2B2B2B",
            dropdown_text_color="white",
            dropdown_hover_color="#575757",
            dropdown_font=("Inter", 16, "bold"),
        )
        self.user_type.grid(row=3, column=0, columnspan=2, pady=(5, 5), padx=(20, 20), sticky="n")

        # Adjusted graph frame with reduced height
        self.graph_frame = CTkFrame(self, width=600, height=100)  # Reduced height
        self.graph_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=(5, 5), sticky='n')

        self.update_nfcid_button = CTkButton(
            self,
            text=self.translations["nfc"]["update_nfcid"],
            width=290,
            height=40,
            font=("Inter", 16, "bold"),
            fg_color="#2B2B2B",
            border_color="white",
            border_width=1,
            hover_color="#333333",
            command=self.show_scan_card,
        )
        self.update_nfcid_button.grid(row=5, column=0, padx=(20, 10), pady=(5, 10))

        self.update_user_button = CTkButton(
            self,
            text=self.translations["admin"]["update_user"],
            width=290,
            height=40,
            text_color="white",
            font=("Inter", 16, "bold"),
            fg_color="#129F07",
            hover_color="#13aF07",
            command=self.update_user,
        )
        self.update_user_button.grid(row=5, column=1, padx=(10, 20), pady=(5, 10))

        self.initialize_user()

    def initialize_user(self):
        logger.debug("Calling initialize_user for user_id=%s", self.user_id)
        user = User.get_by_id(self.session, self.user_id)
        if user:
            name = user.name
            self.nfcid = user.nfcid
            credit = user.credit
            user_type = user.user_type

            logger.debug("User data loaded: name=%s, nfcid=%s, credit=%s, user_type=%s", name, self.nfcid, credit, user_type)

            self.name_entry.insert(0, name)
            self.credits_frame.set_entry_text(credit)
            self.user_type.set(user_type)

            transactions = Transaction.read_all_for_user(self.session, self.user_id)
            logger.debug("Number of transactions found: %d", len(transactions))

            last_month_transactions = self.get_transactions_last_month(transactions)
            logger.debug("Number of transactions in the last month: %d", len(last_month_transactions))

            category_percentages = self.calculate_category_percentage(last_month_transactions)
            logger.debug("Calculated category percentages: %s", category_percentages)

            # Further reduced pie chart size and adjusted to display percentages correctly
            pie_chart = CTkPieChart(self.graph_frame, line_width=15, size=100)  # Adjust size as needed
            pie_chart.pack(side="left", padx=(5, 5), pady=(5, 5))

            for i, (category, percentage) in enumerate(category_percentages.items()):
                if i < len(self.chartColors):
                    color = list(self.chartColors.keys())[i]
                    text_color = self.chartColors[color]
                else:
                    color = None
                    text_color = None

                pie_chart.add(
                    category,
                    percentage,
                    color=color,
                    text_color=text_color,
                    font_size=None  # Let CTkPieChart handle the font size dynamically
                )

            # Adjusted legend to be smaller
            legend_frame = customtkinter.CTkFrame(self.graph_frame, fg_color="transparent")
            legend_frame.pack(side="right", padx=(0, 5), pady=5)

            heading_label = customtkinter.CTkLabel(
                legend_frame,
                text=self.translations["user"]["last_month_purchase"],
                text_color="white",
                font=("Arial", 9, "bold"),
                anchor="w"
            )

            heading_label.pack(side="top", pady=(0, 5))

            for category, values in pie_chart.get().items():
                item_frame = customtkinter.CTkFrame(legend_frame, fg_color="transparent")
                item_frame.pack(fill="x", pady=1, anchor="w")  # Reduced padding for compactness

                color_circle = customtkinter.CTkLabel(
                    item_frame,
                    text="",
                    width=4,
                    height=4,
                    fg_color=values["color"],
                    corner_radius=2
                )
                color_circle.pack(side="left", padx=1)

                category_label = customtkinter.CTkLabel(
                    item_frame,
                    text=category,
                    text_color="white",
                    font=("Arial", 9),
                    anchor="w"
                )
                category_label.pack(side="left")

        else:
            logger.debug("No user found with user_id=%s", self.user_id)

    def get_transactions_last_month(self, transactions):
        logger.debug("Filtering transactions from the last month")
        current_date = datetime.now()
        start_date = current_date - timedelta(days=30)

        filtered_transactions = []
        for transaction in transactions:
            date_transaction = datetime.strptime(transaction[1], "%Y-%m-%d")
            if start_date <= date_transaction <= current_date:
                filtered_transactions.append(transaction)

        logger.debug("Filtered transactions count: %d", len(filtered_transactions))
        return filtered_transactions

    def calculate_category_percentage(self, transactions):
        logger.debug("Calculating category percentages")
        category_totals = {}
        total_amount = sum(float(transaction[2]) for transaction in transactions)

        logger.debug("Total transaction amount: %f", total_amount)

        for transaction in transactions:
            category = transaction[3]
            amount = float(transaction[2])

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
        user_type = self.user_type.get()
        nfcid = self.nfcid.strip()

        logger.debug("Input data: name='%s', nfcid='%s', user_credits='%s', user_type='%s'",
                     name, nfcid, user_credits, user_type)

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
                    user_instance.update(self.session, nfcid=nfcid, name=name, user_type=user_type, credit=user_credits)
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