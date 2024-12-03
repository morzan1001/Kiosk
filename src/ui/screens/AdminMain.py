from customtkinter import *
from PIL import Image, ImageTk
from src.localization.translator import get_translations
from src.ui.screens.UserListing import UserListFrame
from src.ui.screens.ItemListing import ItemListFrame
from src.ui.screens.UserMain import UserMainPage
from src.ui.components.AdminPurchaseItems import AdminPurchaseItemsFrame
from src.ui.components.CountFrame import CountFrame
from src.database import get_db, User, Item
from src.logmgr import logger


class AdminMainFrame(CTkFrame):
    def __init__(self, parent, main_menu, user: User, user_count: int, item_count: int):
        super().__init__(parent)

        self.parent = parent
        self.user_count = user_count
        self.item_count = item_count
        self.user = user
        self.main_menu = main_menu
        self.translations = get_translations()

        self.session = get_db()

        # Configure the grid for the main frame
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        self.configure(width=800, height=480, fg_color="transparent")

        # Load and display the logo image
        self.logo_image = Image.open("src/images/logo.png")
        self.logo_image = self.logo_image.resize((90, 90), Image.Resampling.LANCZOS)
        self.logo_image = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = CTkLabel(self, text="", image=self.logo_image)
        self.logo_label.grid(row=2, column=0, columnspan=3)

        # Display the welcome label
        self.welcome_label = CTkLabel(
            self,
            text=self.translations["admin"]["welcome_admin"],
            text_color="white",
            font=("Inter", 22, "bold"),
        )
        self.welcome_label.grid(row=3, column=0, columnspan=3)

        # Display the user count
        self.user_count_frame = CountFrame(
            self,
            "user-big",
            self.translations["user"]["user"],
            user_count,
            width=270,
            height=135,
            fg_color="white",
        )
        self.user_count_frame.grid(
            row=4, column=0, padx=20, ipadx=30, ipady=20, sticky="e"
        )

        # Display the item count
        self.item_count_frame = CountFrame(
            self,
            "item",
            self.translations["items"]["items"],
            item_count,
            width=270,
            height=135,
            fg_color="white",
        )
        self.item_count_frame.grid(row=4, column=1, padx=20, ipadx=30, ipady=20)

        # Display the item count
        self.item_purchase_frame = AdminPurchaseItemsFrame(
            self,
            "items-list",
            self.translations["items"]["purchase_items"],
            item_count,
            width=270,
            height=135,
            fg_color="white",
        )
        self.item_purchase_frame.grid(
            row=4, column=2, padx=20, ipadx=30, ipady=20, sticky="w"
        )

        # Bind frames to their respective functions
        self.user_count_frame.bind("<Button-1>", self.user_count_clicked)
        self.item_count_frame.bind("<Button-1>", self.item_count_clicked)
        self.item_purchase_frame.bind("<Button-1>", self.item_purchase_clicked)

        # Bind all children of user_count_frame to user_count_clicked
        for child in self.user_count_frame.winfo_children():
            child.bind("<Button-1>", self.user_count_clicked)

        # Bind all children of item_count_frame to item_count_clicked
        for child in self.item_count_frame.winfo_children():
            child.bind("<Button-1>", self.item_count_clicked)

        # Bind all children of item_count_frame to item_count_clicked
        for child in self.item_purchase_frame.winfo_children():
            child.bind("<Button-1>", self.item_purchase_clicked)

    def back_button_pressed(self):
        self.destroy()
        user_count = User.get_count(self.session)
        item_count = Item.get_count(self.session)
        user = User.get_by_id(self.session, self.user.id)
        AdminMainFrame(
            self.parent,
            main_menu=self.main_menu,
            user=user,
            user_count=user_count,
            item_count=item_count,
        )

    def user_count_clicked(self, event):
        logger.debug("User count clicked")
        self.destroy()
        users = User.read_all(self.session)
        UserListFrame(
            self.parent, self.translations["user"]["user_list"], self.back_button_pressed, users=users
        ).grid(row=0, column=0, sticky="ns", ipadx=50, ipady=20)

    def item_count_clicked(self, event):
        logger.debug("Item count clicked")
        self.destroy()
        items = Item.read_all(self.session)
        ItemListFrame(
            self.parent, self.translations["items"]["item_list"], self.back_button_pressed, items
        ).grid(row=0, column=0, sticky="ns", ipadx=50, ipady=20)

    def item_purchase_clicked(self, event):
        logger.debug("Item purchase clicked")
        self.destroy()
        items = Item.read_all(self.session)
        UserMainPage(
            self.parent,
            main_menu=self.main_menu,
            user=self.user,
            items=items
        )