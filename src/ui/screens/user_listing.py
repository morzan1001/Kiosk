"""User listing screen.

Provides a scrollable list of users for admin flows.
"""

import time
from typing import List

from customtkinter import CTkButton, CTkFrame, CTkScrollableFrame

from src.database import User, get_db
from src.localization.translator import get_translations
from src.logmgr import logger
from src.ui.components.heading_frame import HeadingFrame
from src.ui.components.user_frame import UserFrame
from src.ui.navigation import clear_root
from src.ui.screens.new_user import AddUserFrame
from src.ui.screens.update_user import UpdateUserFrame


class UserListFrame(CTkFrame):
    """Screen that lists users and navigates to create/update screens."""

    # Use release instead of press to avoid accidental re-navigation
    # when switching screens (common with touchscreens).
    LEFT_CLICK_EVENT = "<ButtonRelease-1>"

    def __init__(
        self, parent, heading_text: str, back_button_function, users: List[User], *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.back_button_function = back_button_function
        self.heading_text: str = heading_text
        self.translations = get_translations()

        self.session = get_db()

        # Prevent immediate re-navigation caused by the same click/touch event
        # that triggered a screen transition (e.g. back button -> list item click).
        self._nav_lock_until: float = 0.0

        self.configure(width=800, height=480, fg_color="transparent")

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.heading_frame = HeadingFrame(
            self,
            heading_text=self.heading_text,
            back_button_function=self.back_button_function,
            width=760,
            fg_color="transparent",
        )
        self.heading_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="new")

        self.user_list_frame: CTkScrollableFrame | None = None
        self._create_list_frame()
        self._populate_users(users)

        self.add_new_user_button = CTkButton(
            self,
            width=760,
            height=52,
            text=self.translations["admin"]["add_new_user"],
            font=("Inter", 18, "bold"),
            command=self.add_new_user,
        )
        self.add_new_user_button.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

    def _create_list_frame(self) -> None:
        """Create (or recreate) the scrollable list container."""
        if self.user_list_frame is not None and self.user_list_frame.winfo_exists():
            self.user_list_frame.destroy()

        self.user_list_frame = CTkScrollableFrame(self, width=760, height=300, fg_color="white")
        self.user_list_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        self.user_list_frame.grid_columnconfigure(0, weight=1)

    def _populate_users(self, users: List[User]) -> None:
        """Populate the scrollable list with user rows and bindings."""
        if self.user_list_frame is None:
            return

        for i in range(len(users)):
            self.user_list_frame.grid_rowconfigure(i, weight=1)

        for indx, user in enumerate(users):
            sub_frame = CTkFrame(self.user_list_frame, fg_color="white", width=740, height=60)
            sub_frame.grid(row=indx, column=0, padx=10, pady=10, sticky="nsew")

            # Configure grid for sub_frame
            sub_frame.grid_rowconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(1, weight=1)

            # Add widgets to the sub_frame
            user_frame = UserFrame(
                sub_frame, data=(user.id, user.name, user.credit), fg_color="white"
            )
            user_frame.grid(row=0, column=0, sticky="w")

            sub_frame.bind(
                self.LEFT_CLICK_EVENT,
                lambda event, user_id=user.id: self.update_user(event, user_id),
            )

            user_frame.bind(
                self.LEFT_CLICK_EVENT,
                lambda event, user_id=user.id: self.update_user(event, user_id),
            )

            for child in sub_frame.winfo_children():
                child.bind(
                    self.LEFT_CLICK_EVENT,
                    lambda event, user_id=user.id: self.update_user(event, user_id),
                )

            for child in user_frame.winfo_children():
                child.bind(
                    self.LEFT_CLICK_EVENT,
                    lambda event, user_id=user.id: self.update_user(event, user_id),
                )

    def update_user(self, _event, user_id):
        """Navigate to the update-user screen for the selected user."""
        now = time.monotonic()
        if now < self._nav_lock_until:
            return

        # Lock immediately to avoid creating multiple frames on double-tap.
        self._nav_lock_until = now + 1.0

        try:
            clear_root(self.parent)

            def back_to_list() -> None:
                self.return_to_user_listing()

            update_user_frame = UpdateUserFrame(self.parent, back_to_list, user_id)
            update_user_frame.grid(row=0, column=0, sticky="nsew")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception(
                "Opening update-user screen failed | list=%s user_id=%s",
                id(self),
                user_id,
            )
            raise

    def return_to_user_listing(self):
        """Recreate this listing screen after returning from a sub-screen."""
        clear_root(self.parent)
        users: List[User] = User.read_all(self.session)
        UserListFrame(
            self.parent,
            self.heading_text,
            self.back_button_function,
            users=users,
            width=800,
            height=480,
            fg_color="transparent",
        ).grid(row=0, column=0, sticky="nsew")

    def _show_listing(self) -> None:
        # Deprecated with single-screen navigation (kept for compatibility if called).
        users: List[User] = User.read_all(self.session)
        self._create_list_frame()
        self._populate_users(users)
        self.grid(row=0, column=0, sticky="nsew")

    def add_new_user(self):
        """Navigate to the add-user screen."""
        now = time.monotonic()
        if now < self._nav_lock_until:
            return

        # Lock immediately to avoid creating multiple frames on double-tap.
        self._nav_lock_until = now + 1.0
        try:
            clear_root(self.parent)

            def back_to_list() -> None:
                self.return_to_user_listing()

            new_user_frame = AddUserFrame(
                self.parent,
                back_button_function=back_to_list,
                width=800,
                height=480,
                fg_color="transparent",
            )
            new_user_frame.grid(row=0, column=0, sticky="nsew")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Opening add-user screen failed | list=%s", id(self))
            raise
