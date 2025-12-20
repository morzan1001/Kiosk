from customtkinter import (CTkButton, CTkEntry, CTkFrame, CTkLabel,
                           CTkOptionMenu)

from src.database import User, get_db
from src.localization.translator import get_translations
from src.ui.components.credit_frame import CreditFrame
from src.ui.components.heading_frame import HeadingFrame
from src.ui.components.message import ShowMessage
from src.ui.components.scan_card import ScanCardFrame


class AddUserFrame(CTkFrame):
    def __init__(self, parent, back_button_function, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.back_button_function = back_button_function
        self.translations = get_translations()
        self.nfcid: str = ""

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        heading_frame = HeadingFrame(
            self,
            heading_text=self.translations["admin"]["add_new_user"],
            back_button_function=back_button_function,
            width=600,
            fg_color="transparent",
        )
        heading_frame.grid(row=0, column=0, columnspan=2, padx=10, sticky="new")

        # Inventory label
        credits_label = CTkLabel(
            self,
            text=self.translations["user"]["credits_label"],
            width=290,
            anchor="w",
            font=("Arial", 18, "bold"),
        )
        credits_label.grid(row=2, column=1, pady=(10, 0), sticky="s")

        # Name entry
        self.name_entry = CTkEntry(
            self,
            placeholder_text=self.translations["user"]["enter_name"],
            width=290,
            height=50,
            corner_radius=10,
            font=("Inter", 18, "bold"),
        )
        self.name_entry.grid(row=3, column=0, padx=(20, 10))

        # Inventory entry with buttons
        self.credits_frame = CreditFrame(
            self,
            width=290,
            height=60,
            corner_radius=10,
            border_width=2,
        )
        self.credits_frame.grid(
            row=3, column=1, padx=(10, 20), pady=(10, 10), sticky="w"
        )

        self.type = CTkOptionMenu(
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
        self.type.grid(
            row=4, column=0, columnspan=2, pady=(10, 10), padx=(20, 20), sticky="n"
        )

        # Update NFCID button
        self.update_nfcid_button = CTkButton(
            self,
            text=self.translations["nfc"]["add_nfcid"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.show_scan_card,
        )
        self.update_nfcid_button.grid(row=5, column=0, padx=(20, 10), pady=(20, 10))

        # Update Details button
        self.add_item_button = CTkButton(
            self,
            text=self.translations["admin"]["add_new_user"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            state="disabled",
            command=self.add_user,
        )
        self.add_item_button.grid(row=5, column=1, padx=(10, 10), pady=(20, 10))
        self.enable_add_user_button()

    def show_scan_card(self):
        # Create and place the main frame
        self.scan_card_frame = ScanCardFrame(
            parent=self.parent,
            heading_text=self.translations["nfc"]["add_nfcid"],
            set_nfcid_id=self.set_nfcid,
            back_button_function=self.remove_scan_card,
        )
        self.scan_card_frame.grid(row=0, column=0, sticky="nsew")

    def remove_scan_card(self):
        self.scan_card_frame.destroy()

    def enable_add_user_button(self):
        self.add_item_button.configure(state="normal")

    def add_user(self):
        name = self.name_entry.get()
        user_credits = self.credits_frame.get()
        type = self.type.get()
        nfcid = self.nfcid

        if not (name and nfcid):
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["admin"]["error_adding_user"],
                text=self.translations["admin"]["missing_nfcid_name"],
            )
            self.parent.after(5000, self.message.destroy)

            return

        # Check if a user with the same NFC ID already exists
        existing_user = User.get_by_nfcid(self.session, nfcid)
        if existing_user:
            # Show message if user already exists
            self.message = ShowMessage(
                self.parent,
                image="unsuccessful",
                heading=self.translations["admin"]["error_adding_user"],
                text=self.translations["nfc"]["card_already_used"],
            )
            self.parent.after(5000, self.message.destroy)
        else:
            # Create a new User instance
            new_user = User(nfcid=nfcid, name=name, type=type, credit=user_credits)

        # Save the new user to the database
        new_user.create(self.session)

        self.back_button_function()

    def set_nfcid(self, new_nfcid):
        self.nfcid = new_nfcid
