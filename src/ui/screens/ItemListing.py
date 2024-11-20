from typing import List
from customtkinter import *
from src.localization.translator import get_translations
from src.ui.components.HeadingFrame import HeadingFrame
from src.ui.screens.NewItem import AddNewItemFrame
from src.ui.screens.UpdateItem import UpdateItemFrame
from src.ui.components.ItemFrame import ItemFrame
from src.database import get_db, Item

class ItemListFrame(CTkFrame):
    def __init__(
        self, parent, heading_text: str, back_button_function: function, items: List[Item], *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.heading_text: str = heading_text
        self.back_button_function: function = back_button_function
        self.translations = get_translations()
        self.items: List[Item] = items

        self.session = get_db()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.configure(width=800, height=480, fg_color="transparent")

        self.heading_frame = HeadingFrame(
            self,
            heading_text=self.heading_text,
            back_button_function=self.back_button_function,
            width=600,
            fg_color="transparent",
        )
        self.heading_frame.grid(row=0, column=0, sticky="new", padx=90, pady=(20, 0))

        self.item_list_frame = CTkScrollableFrame(
            self, width=580, height=300, fg_color="white"
        )
        self.item_list_frame.grid(row=1, column=0, padx=50, pady=20)

        self.item_list_frame.grid_columnconfigure(0, weight=1)

        for i in range(len(self.items)):
            self.item_list_frame.grid_rowconfigure(i, weight=1)

        # Add frames for items
        for indx, item in enumerate(self.items):
            sub_frame = CTkFrame(
                self.item_list_frame, fg_color="white", width=580, height=60
            )
            sub_frame.grid(row=indx, column=0, padx=10, pady=10, sticky="nsew")

            # Configure grid for sub_frame
            sub_frame.grid_rowconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(0, weight=1)
            sub_frame.grid_columnconfigure(1, weight=1)

            # Add widgets to the sub_frame
            item_frame = ItemFrame(
                sub_frame, data=item, fg_color="white"
            )
            item_frame.grid(row=0, column=0, sticky="w")

            sub_frame.bind(
                "<Button-1>",
                lambda event, item_id=item.id: self.update_item(event, item_id),
            )

            item_frame.bind(
                "<Button-1>",
                lambda event, item_id=item.id: self.update_item(event, item_id),
            )

            # Bind all children of sub_frame to update_item
            for child in sub_frame.winfo_children():
                child.bind(
                    "<Button-1>",
                    lambda event, item_id=item.id: self.update_item(event, item_id),
                )

            # Bind all children of item_frame to update_item
            for child in item_frame.winfo_children():
                child.bind(
                    "<Button-1>",
                    lambda event, item_id=item.id: self.update_item(event, item_id),
                )

        self.add_new_item_button = CTkButton(
            self,
            width=600,
            height=52,
            text=self.translations["items"]["add_new_item"],
            fg_color="#129F07",
            hover_color="#13aF07",
            font=("Inter", 18, "bold"),
            command=self.add_new_item,
        )
        self.add_new_item_button.grid(row=2, column=0, pady=10)

    def return_to_items_listing(self):
        all_items: List[Item] = Item.read_all(self.session)
        ItemListFrame(
            self.parent, self.heading_text, self.back_button_function, all_items
        ).grid(row=0, column=0, sticky="ns", ipadx=50, ipady=20)
        if hasattr(self, "new_item_frame"):
            self.new_item_frame.destroy()

    def add_new_item(self):
        self.destroy()
        self.new_item_frame = AddNewItemFrame(
            self.parent,
            back_button_function=self.return_to_items_listing,
            width=800,
            height=480,
        )
        self.new_item_frame.grid(row=0, column=0, sticky="ns")

    def update_item(self, event, item_id: int):
        self.destroy()
        self.new_item_frame = UpdateItemFrame(
            self.parent,
            back_button_function=self.return_to_items_listing,
            item_id=item_id,
            width=800,
            height=480,
        )
        self.new_item_frame.grid(row=0, column=0, sticky="ns")