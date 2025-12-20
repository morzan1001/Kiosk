import logging

from customtkinter import CTkButton, CTkFrame

from src.database import User, get_db
from src.localization.translator import get_translations
from src.ui.components.heading_frame import HeadingFrame
from src.ui.components.message import ShowMessage
from src.ui.components.user_form import UserForm

logger = logging.getLogger(__name__)


class AddUserFrame(CTkFrame):
    def __init__(self, parent, back_button_function, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        logger.debug("Initializing AddUserFrame")

        self.parent = parent
        self.back_button_function = back_button_function
        self.translations = get_translations()

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        heading_frame = HeadingFrame(
            self,
            heading_text=self.translations["admin"]["add_new_user"],
            back_button_function=back_button_function,
            width=600,
            fg_color="transparent",
        )
        heading_frame.grid(row=0, column=0, columnspan=2, padx=10, sticky="new")

        # User Form
        self.user_form = UserForm(self, parent_screen=self.parent)
        self.user_form.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Add User Button
        self.add_user_button = CTkButton(
            self.user_form,
            text=self.translations["admin"]["add_new_user"],
            width=290,
            height=50,
            font=("Inter", 18, "bold"),
            command=self.add_user,
        )
        self.add_user_button.grid(row=3, column=1, padx=(10, 10), pady=(20, 10), sticky="w")

    def add_user(self):
        logger.debug("Attempting to add new user")
        data = self.user_form.get_data()
        name = data["name"]
        user_credits = data["credit"]
        user_type = data["type"]
        nfcid = data["nfcid"]

        if not (name and nfcid):
            logger.warning("Name or NFCID missing")
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
            logger.warning("User with NFCID %s already exists", nfcid)
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
            logger.info("Creating new user: %s", name)
            new_user = User(nfcid=nfcid, name=name, type=user_type, credit=user_credits)

        # Save the new user to the database
        new_user.create(self.session)
        logger.info("User created successfully")

        self.back_button_function()
