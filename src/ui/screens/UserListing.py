from customtkinter import *
from src.localization.translator import get_translations
from .NewUser import AddUserFrame
from .UpdateUser import UpdateUserFrame
from src.database import get_db, User
from src.ui.components.HeadingFrame import HeadingFrame
from src.ui.components.UserFrame import UserFrame

class UserListFrame(CTkFrame):
    def __init__(
        self, parent, heading_text, back_button_function, data, *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.back_button_function = back_button_function
        self.heading_text = heading_text
        self.translations = get_translations()

        self.session = get_db()

        self.configure(width=800, height=480, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.heading_frame = HeadingFrame(
            self,
            heading_text=self.heading_text,
            back_button_function=self.back_button_function,
            width=600,
            fg_color="transparent",
        )
        self.heading_frame.grid(row=0, column=0, sticky="new", padx=90, pady=(20, 0))

        self.user_list_frame = CTkScrollableFrame(
            self, width=580, height=300, fg_color="white"
        )
        self.user_list_frame.grid(row=1, column=0, padx=50, pady=20)

        self.user_list_frame.grid_columnconfigure(0, weight=1)

        for i in range(len(data)):
            self.user_list_frame.grid_rowconfigure(i, weight=1)

        # Add frames for users
        for indx, user in enumerate(data):
            sub_frame = CTkFrame(
                self.user_list_frame, fg_color="white", width=580, height=60
            )
            sub_frame.grid(row=indx, column=0, padx=10, pady=10, sticky="nsew")

            # Configure grid for sub_frame
            sub_frame.grid_rowconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(1, weight=1)

            # Add widgets to the sub_frame
            user_frame = UserFrame(
                sub_frame, data=(user[0], user[1], user[2]), fg_color="white"
            )
            user_frame.grid(row=0, column=0, sticky="w")

            sub_frame.bind(
                "<Button-1>",
                lambda event, user_id=user[0]: self.update_user(event, user_id),
            )

            user_frame.bind(
                "<Button-1>",
                lambda event, user_id=user[0]: self.update_user(event, user_id),
            )

            # Bind all children of user_count_frame to user_count_clicked
            for child in sub_frame.winfo_children():
                child.bind("<Button-1>", lambda event, user_id=user[0]: self.update_user(event, user_id))

            for child in user_frame.winfo_children():
                child.bind("<Button-1>", lambda event, user_id=user[0]: self.update_user(event, user_id))

        self.add_new_user_button = CTkButton(
            self,
            width=600,
            height=52,
            text=self.translations["admin"]["add_new_user"],
            fg_color="#129F07",
            hover_color="#13aF07",
            font=("Inter", 18, "bold"),
            command=self.add_new_user,
        )
        self.add_new_user_button.grid(row=2, column=0, pady=10)

    def update_user(self, event, user_id):
        self.destroy()
        self.update_user_frame = UpdateUserFrame(
            self.parent,
            back_button_function=self.return_to_user_listing,
            user_id=user_id,
            width=800,
            height=480,
            fg_color="transparent",
        )
        self.update_user_frame.grid(row=0, column=0, sticky="ns")

    def return_to_user_listing(self):
        users = User.read_all(self.session)
        UserListFrame(
            self.parent, self.heading_text, self.back_button_function, users
        ).grid(row=0, column=0, sticky="ns", ipadx=50, ipady=20)
        
        if hasattr(self, "new_user_frame"):
            self.new_user_frame.destroy()
        
        if hasattr(self, "update_user_frame"):
            self.update_user_frame.destroy()

    def add_new_user(self):
        self.destroy()
        self.new_user_frame = AddUserFrame(
            self.parent,
            back_button_function=self.return_to_user_listing,
            width=800,
            height=480,
            fg_color="transparent",
        )
        self.new_user_frame.grid(row=0, column=0, sticky="ns")