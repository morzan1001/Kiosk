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

class UpdateUserFrame(CTkFrame):
    def __init__(self, parent, back_button_function, user_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.chartColors = {"#0FD600": "white", "#EA68FF": "white", "#E8AF1A": "white"}

        self.parent = parent
        self.back_button_function = back_button_function
        self.user_id = user_id
        self.translations = get_translations()
        self.nfcid = ""

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

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
            font=("Inter", 18, "bold"),
        )
        credits_label.grid(row=2, column=1, sticky="s", pady=(10, 10))

        self.name_entry = CTkEntry(
            self,
            placeholder_text=self.translations["user"]["enter_name"],
            width=290,
            height=50,
            border_color="#656565",
            fg_color="#202020",
            corner_radius=10,
            text_color="white",
            font=("Inter", 18, "bold"),
        )
        self.name_entry.grid(row=3, column=0, padx=(20, 10), pady=(10, 10))

        self.credits_frame = CreditFrame(
            self,
            width=290,
            height=60,
            fg_color="#1C1C1C",
            corner_radius=10,
            border_width=2,
            border_color="#5D5D5D",
        )
        self.credits_frame.grid(row=3, column=1, padx=(10, 20), pady=(10, 10), sticky="w")

        self.user_type = CTkOptionMenu(
            self,
            values=[self.translations["user"]["user"], self.translations["admin"]["admin"]],
            width=620,
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
        self.user_type.grid(row=4, column=0, columnspan=2, pady=(10, 10), padx=(20, 20), sticky="n")

        self.graph_frame = CTkFrame(self, width=610, height=50)
        self.graph_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=(10, 10))

        self.update_nfcid_button = CTkButton(
            self,
            text=self.translations["nfc"]["update_nfcid"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            fg_color="#2B2B2B",
            border_color="white",
            border_width=1,
            hover_color="#333333",
            command=self.show_scan_card,
        )
        self.update_nfcid_button.grid(row=6, column=0, padx=(20, 10), pady=(10, 10))

        self.update_user_button = CTkButton(
            self,
            text=self.translations["admin"]["update_user"],
            width=290,
            height=50,
            text_color="white",
            font=("Inter", 18, "bold"),
            fg_color="#129F07",
            hover_color="#13aF07",
            command=self.update_user,
        )
        self.update_user_button.grid(row=6, column=1, padx=(10, 20), pady=(10, 10))

        self.initialize_user()

    def initialize_user(self):
        user = User.get_by_id(self.session, self.user_id)
        name = user.name
        self.nfcid = user.nfcid
        credit = user.credit
        user_type = user.user_type

        self.name_entry.insert(0, name)
        self.credits_frame.set_entry_text(credit)
        self.user_type.set(user_type)

        transactions = Transaction.read_all_for_user(self.session, self.user_id)

        last_month_transactions = self.get_transactions_last_month(transactions)
        category_percentages = self.calculate_category_percentage(last_month_transactions)

        pie_chart = CTkPieChart(self.graph_frame, line_width=50)
        pie_chart.pack(side="left", padx=(50, 30), pady=(10, 20))

        for i, (category, percentage) in enumerate(category_percentages.items()):
            if i < len(self.chartColors):
                color = list(self.chartColors.keys())[i]
                text_color = self.chartColors[color]
            else:
                color = None
                text_color = None

            if percentage <= 15:
                percent_font_size = 60
            elif percentage <= 30:
                percent_font_size = 80
            else:
                percent_font_size = 100
            percent_font_size = 60

            pie_chart.add(category, percentage, color=color, text_color=text_color, font_size=percent_font_size)

        legend_frame = customtkinter.CTkFrame(self.graph_frame, fg_color="transparent")
        legend_frame.pack(side="right", padx=(0, 10), pady=10)

        heading_label = customtkinter.CTkLabel(
            legend_frame,
            text=self.translations["user"]["last_month_purchase"],
            text_color="white",
            font=("Arial", 14, "bold"),
            anchor="w"
        )

        heading_label.pack(side="top", pady=(0, 10))

        for category, values in pie_chart.get().items():
            item_frame = customtkinter.CTkFrame(legend_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=5, anchor="w")

            color_circle = customtkinter.CTkLabel(
                item_frame,
                text="",
                width=10,
                height=10,
                fg_color=values["color"],
                corner_radius=4
            )
            color_circle.pack(side="left", padx=5)

            category_label = customtkinter.CTkLabel(
                item_frame,
                text=category,
                text_color="white",
                anchor="w"
            )
            category_label.pack(side="left")

    def get_transactions_last_month(self, transactions):
        current_date = datetime.now()
        start_date = current_date - timedelta(days=30)

        filtered_transactions = []
        for transaction in transactions:
            date_transaction = datetime.strptime(transaction[1], "%Y-%m-%d")
            if start_date <= date_transaction <= current_date:
                filtered_transactions.append(transaction)

        return filtered_transactions

    def calculate_category_percentage(self, transactions):
        category_totals = {}
        total_amount = sum(float(transaction[2]) for transaction in transactions)

        for transaction in transactions:
            category = transaction[3]
            amount = float(transaction[2])

            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        category_percentages = {
            category: (amount / total_amount) * 100
            for category, amount in category_totals.items()
        }

        return category_percentages

    def show_scan_card(self):
        self.nfcid = ""
        self.scan_card_frame = ScanCardFrame(
            parent=self.parent,
            heading_text=self.translations["nfc"]["update_nfcid"],
            set_nfcid_id=self.set_nfcid_id,
            back_button_function=self.remove_scan_card,
        )
        self.scan_card_frame.grid(row=0, column=0, sticky="nsew")

    def remove_scan_card(self):
        self.scan_card_frame.destroy()

    def update_user(self):
        name = self.name_entry.get()
        user_credits = self.credits_frame.get()
        user_type = self.user_type.get()
        nfcid = self.nfcid
        if not (name and nfcid):
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["admin"]["error_updating_user"],
                text=self.translations["admin"]["missing_nfcid_name"],
            )
            self.parent.after(5000, self.message.destroy)
            return        

        existing_user = User.get_by_nfcid(self.session, nfcid)
        if existing_user:
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["admin"]["error_updating_user"],
                text=self.translations["nfc"]["card_already_used"],
            )
            self.parent.after(5000, self.message.destroy)
        else:
            user_instance = User.get_by_id(self.session, self.user_id)

            if user_instance:
                user_instance.update(self.session, nfcid=nfcid, name=name, user_type=user_type, credit=user_credits)

        self.back_button_function()

    def set_nfcid_id(self, new_nfcid):
        self.nfcid = new_nfcid

    def confirm_delete(self):
        user_instance = User.get_by_id(self.session, self.user_id)
        if user_instance:
            user_instance.delete(self.session)

        self.back_button_function()

    def delete_user(self):
        DeleteConfirmation(self.parent, self.confirm_delete, self.translations["user"]["user"])