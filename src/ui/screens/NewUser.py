from customtkinter import *
from src.localization.translator import get_translations
from src.database import get_db, User
from src.ui.components.HeadingFrame import HeadingFrame
from src.ui.components.ScanCard import ScanCardFrame
from src.ui.components.CreditFrame import CreditFrame
from src.ui.components.Message import ShowMessage


class AddUserFrame(CTkFrame):
    def __init__(self, parent, back_button_function: function, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.back_button_function: function = back_button_function
        self.translations = get_translations()
        self.nfcid: str = ""

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        heading_frame = HeadingFrame(
            self, self.translations["admin"]["add_new_user"], back_button_function=back_button_function
        )
        heading_frame.grid(row=0, column=0, columnspan=2, padx=40, sticky="new")

        # Inventory label
        credits_label = CTkLabel(
            self,
            text=self.translations["user"]["credits_label"],
            width=290,
            anchor="w",
            text_color="white",
            font=("Arial", 18, "bold"),
        )
        credits_label.grid(row=2, column=1, pady=(10, 0), sticky="s")

        # Name entry
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
        self.name_entry.grid(row=3, column=0, padx=(20, 10))

        # Inventory entry with buttons
        self.credits_frame = CreditFrame(
            self,
            width=290,
            height=60,
            fg_color="#1C1C1C",
            corner_radius=10,
            border_width=2,
            border_color="#5D5D5D",
        )
        self.credits_frame.grid(
            row=3, column=1, padx=(10, 20), pady=(10, 10), sticky="w"
        )

        self.type = CTkOptionMenu(
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
        self.type.grid(row=4, column=0, columnspan=2, pady=(10, 10), padx=(20, 20), sticky="n")

        # Update NFCID button
        self.update_nfcid_button = CTkButton(
            self,
            text=self.translations["nfc"]["add_nfcid"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            fg_color="#2B2B2B",
            border_color="white",
            border_width=1,
            hover_color="#333333",
            command=self.show_scan_card,
        )
        self.update_nfcid_button.grid(row=5, column=0, padx=(20, 10), pady=(20, 10))

        # Update Details button
        self.add_item_button = CTkButton(
            self,
            text=self.translations["admin"]["add_new_user"],
            width=290,
            height=50,
            text_color="white",
            font=("Inter", 18, "bold"),
            fg_color="#494949",
            hover_color="#13aF07",
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
        self.add_item_button.configure(fg_color="#129F07")
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
            new_user = User(
                nfcid=nfcid, name=name, type=type, credit=user_credits
            )

        # Save the new user to the database
        new_user.create(self.session)

        self.back_button_function()

    def set_nfcid(self, new_nfcid):
        self.nfcid = new_nfcid