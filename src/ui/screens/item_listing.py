"""Item listing screen.

Provides a scrollable list of items for admin flows.
"""

import time
from typing import List

from customtkinter import CTkButton, CTkFrame, CTkScrollableFrame

from src.database import Item, get_db
from src.localization.translator import get_translations
from src.logmgr import logger
from src.ui.components.heading_frame import HeadingFrame
from src.ui.components.item_frame import ItemFrame
from src.ui.navigation import clear_root
from src.ui.screens.new_item import AddNewItemFrame
from src.ui.screens.update_item import UpdateItemFrame


class ItemListFrame(CTkFrame):
    """Screen that lists items and navigates to create/update screens."""

    # Use release instead of press to avoid accidental re-navigation
    # when switching screens (common with touchscreens).
    LEFT_CLICK_EVENT = "<ButtonRelease-1>"

    def __init__(
        self, parent, heading_text: str, back_button_function, items: List[Item], *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.heading_text: str = heading_text
        self.back_button_function = back_button_function
        self.translations = get_translations()
        self.items: List[Item] = items

        self.session = get_db()

        # Prevent immediate re-navigation caused by the same click/touch event
        # that triggered a screen transition (e.g. back button -> list item click).
        self._nav_lock_until: float = 0.0

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.configure(width=800, height=480, fg_color="transparent")

        self.heading_frame = HeadingFrame(
            self,
            heading_text=self.heading_text,
            back_button_function=self.back_button_function,
            width=760,
            fg_color="transparent",
        )
        self.heading_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="new")

        self.item_list_frame: CTkScrollableFrame | None = None
        self._create_list_frame()
        self._populate_items(self.items)

        self.add_new_item_button = CTkButton(
            self,
            width=760,
            height=52,
            text=self.translations["items"]["add_new_item"],
            font=("Inter", 18, "bold"),
            command=self.add_new_item,
        )
        self.add_new_item_button.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

    def _create_list_frame(self) -> None:
        """Create (or recreate) the scrollable list container."""
        if self.item_list_frame is not None and self.item_list_frame.winfo_exists():
            self.item_list_frame.destroy()

        self.item_list_frame = CTkScrollableFrame(self, width=760, height=300, fg_color="white")
        self.item_list_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        self.item_list_frame.grid_columnconfigure(0, weight=1)

    def _populate_items(self, items: List[Item]) -> None:
        """Populate the scrollable list with item rows and bindings."""
        if self.item_list_frame is None:
            return

        for i in range(len(items)):
            self.item_list_frame.grid_rowconfigure(i, weight=1)

        for indx, item in enumerate(items):
            sub_frame = CTkFrame(self.item_list_frame, fg_color="white", width=740, height=60)
            sub_frame.grid(row=indx, column=0, padx=10, pady=10, sticky="nsew")

            # Configure grid for sub_frame
            sub_frame.grid_rowconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(1, weight=1)

            # Add widgets to the sub_frame
            item_frame = ItemFrame(sub_frame, data=item, fg_color="white")
            item_frame.grid(row=0, column=0, sticky="w")

            sub_frame.bind(
                self.LEFT_CLICK_EVENT,
                lambda event, item_id=item.id: self.update_item(event, item_id),
            )

            item_frame.bind(
                self.LEFT_CLICK_EVENT,
                lambda event, item_id=item.id: self.update_item(event, item_id),
            )

            # Bind all children of sub_frame to update_item
            for child in sub_frame.winfo_children():
                child.bind(
                    self.LEFT_CLICK_EVENT,
                    lambda event, item_id=item.id: self.update_item(event, item_id),
                )

            # Bind all children of item_frame to update_item
            for child in item_frame.winfo_children():
                child.bind(
                    self.LEFT_CLICK_EVENT,
                    lambda event, item_id=item.id: self.update_item(event, item_id),
                )

    def return_to_items_listing(self):
        """Recreate this listing screen after returning from a sub-screen."""
        clear_root(self.parent)
        items = Item.read_all(self.session)
        ItemListFrame(
            self.parent,
            self.heading_text,
            self.back_button_function,
            items,
            width=800,
            height=480,
            fg_color="transparent",
        ).grid(row=0, column=0, sticky="nsew")

    def _show_listing(self) -> None:
        # Deprecated with single-screen navigation (kept for compatibility if called).
        self.items = Item.read_all(self.session)
        self._create_list_frame()
        self._populate_items(self.items)
        self.grid(row=0, column=0, sticky="nsew")

    def add_new_item(self):
        """Navigate to the add-item screen."""
        now = time.monotonic()
        if now < self._nav_lock_until:
            return

        # Lock immediately to avoid creating multiple frames on double-tap.
        self._nav_lock_until = now + 1.0
        try:
            clear_root(self.parent)

            def back_to_list() -> None:
                self.return_to_items_listing()

            new_item_frame = AddNewItemFrame(
                self.parent,
                back_button_function=back_to_list,
                width=800,
                height=480,
            )
            new_item_frame.grid(row=0, column=0, sticky="nsew")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Opening add-item screen failed | list=%s", id(self))
            raise

    def update_item(self, _event, item_id: int):
        """Navigate to the update-item screen for the selected item."""
        now = time.monotonic()
        if now < self._nav_lock_until:
            return

        # Lock immediately to avoid creating multiple frames on double-tap.
        self._nav_lock_until = now + 1.0

        try:
            clear_root(self.parent)

            def back_to_list() -> None:
                self.return_to_items_listing()

            update_item_frame = UpdateItemFrame(
                self.parent,
                back_button_function=back_to_list,
                item_id=item_id,
                width=800,
                height=480,
            )
            update_item_frame.grid(row=0, column=0, sticky="nsew")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception(
                "Opening update-item screen failed | list=%s item_id=%s",
                id(self),
                item_id,
            )
            raise
