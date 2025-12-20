from customtkinter import CTkButton, CTkEntry, CTkFrame, CTkLabel, CTkOptionMenu

from src.localization.translator import get_translations
from src.ui.components.credit_frame import CreditFrame
from src.ui.components.scan_card import ScanCardFrame


class UserForm(CTkFrame):
    def __init__(self, master, parent_screen, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.parent_screen = parent_screen
        self.translations = get_translations()
        self.nfcid: str = ""

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.configure(fg_color="transparent")

        # Credits label
        self.credits_label = CTkLabel(
            self,
            text=self.translations["user"]["credits_label"],
            width=290,
            anchor="w",
            font=("Arial", 18, "bold"),
        )
        self.credits_label.grid(row=0, column=1, pady=(10, 0), sticky="s")

        # Name entry
        self.name_entry = CTkEntry(
            self,
            placeholder_text=self.translations["user"]["enter_name"],
            width=290,
            height=50,
            corner_radius=10,
            font=("Inter", 18, "bold"),
        )
        self.name_entry.grid(row=1, column=0, padx=(20, 10), sticky="e")

        # Credits frame
        self.credits_frame = CreditFrame(
            self,
            width=290,
            height=60,
            corner_radius=10,
            border_width=2,
        )
        self.credits_frame.grid(row=1, column=1, padx=(10, 20), pady=(10, 10), sticky="w")

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
            row=2, column=0, columnspan=2, pady=(10, 10), padx=(20, 20), sticky="n"
        )

        # NFCID button
        self.nfcid_button = CTkButton(
            self,
            text=self.translations["nfc"]["add_nfcid"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.show_scan_card,
        )
        self.nfcid_button.grid(row=3, column=0, padx=(20, 10), pady=(20, 10), sticky="e")

    def show_scan_card(self):
        self.scan_card_frame = ScanCardFrame(
            parent=self.parent_screen,
            heading_text=self.translations["nfc"]["add_nfcid"],
            set_nfcid_id=self.set_nfcid,
            back_button_function=self.remove_scan_card,
        )
        self.scan_card_frame.grid(row=0, column=0, sticky="nsew")

    def remove_scan_card(self):
        if hasattr(self, "scan_card_frame"):
            self.scan_card_frame.destroy()

    def set_nfcid(self, new_nfcid):
        self.nfcid = new_nfcid

    def get_data(self):
        return {
            "name": self.name_entry.get(),
            "credit": self.credits_frame.get(),
            "type": self.user_type_menu.get(),
            "nfcid": self.nfcid,
        }

    def set_data(self, name, credit, user_type, nfcid):
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, name)

        self.credits_frame.set_entry_text(str(credit))

        self.user_type_menu.set(user_type)

        self.nfcid = nfcid
