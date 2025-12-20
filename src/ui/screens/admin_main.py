from customtkinter import CTkFrame, CTkImage, CTkLabel
from PIL import Image

from src.database import Item, User, get_db
from src.localization.translator import get_translations
from src.logmgr import logger
from src.ui.components.dashboard_card_frame import DashboardCardFrame
from src.ui.screens.item_listing import ItemListFrame
from src.ui.screens.user_listing import UserListFrame
from src.ui.screens.user_main import UserMainPage
from src.utils.paths import get_image_path


class AdminMainFrame(CTkFrame):
    LEFT_CLICK_EVENT = "<Button-1>"

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

        # Load and display the logo image using CTkImage
        logo_image = Image.open(get_image_path("logo.png"))
        self.logo_image = CTkImage(light_image=logo_image, dark_image=logo_image, size=(90, 90))
        self.logo_label = CTkLabel(self, text="", image=self.logo_image)
        self.logo_label.grid(row=2, column=0, columnspan=3)

        # Display the welcome label
        self.welcome_label = CTkLabel(
            self,
            text=self.translations["admin"]["welcome_admin"],
            font=("Inter", 22, "bold"),
        )
        self.welcome_label.grid(row=3, column=0, columnspan=3)

        # Display the user count
        self.user_count_frame = DashboardCardFrame(
            self,
            title=self.translations["user"]["user"],
            image_filename="user-big",
            value=str(user_count),
            width=270,
            height=135,
        )
        self.user_count_frame.grid(row=4, column=0, padx=20, ipadx=30, ipady=20, sticky="e")

        # Display the item count
        self.item_count_frame = DashboardCardFrame(
            self,
            title=self.translations["items"]["items"],
            image_filename="item",
            value=str(item_count),
            width=270,
            height=135,
        )
        self.item_count_frame.grid(row=4, column=1, padx=20, ipadx=30, ipady=20)

        # Display the item purchase button (no value, just title)
        self.item_purchase_frame = DashboardCardFrame(
            self,
            title=self.translations["items"]["purchase_items"],
            image_filename="items-list",
            value=None,
            width=270,
            height=135,
        )
        self.item_purchase_frame.grid(row=4, column=2, padx=20, ipadx=30, ipady=20, sticky="w")

        # Bind frames to their respective functions
        self.user_count_frame.bind(self.LEFT_CLICK_EVENT, self.user_count_clicked)
        self.item_count_frame.bind(self.LEFT_CLICK_EVENT, self.item_count_clicked)
        self.item_purchase_frame.bind(self.LEFT_CLICK_EVENT, self.item_purchase_clicked)

        # Bind all children of user_count_frame to user_count_clicked
        for child in self.user_count_frame.winfo_children():
            child.bind(self.LEFT_CLICK_EVENT, self.user_count_clicked)

        for child in self.item_count_frame.winfo_children():
            child.bind(self.LEFT_CLICK_EVENT, self.item_count_clicked)

        for child in self.item_purchase_frame.winfo_children():
            child.bind(self.LEFT_CLICK_EVENT, self.item_purchase_clicked)

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
            self.parent,
            self.translations["user"]["user_list"],
            self.back_button_pressed,
            users=users,
        ).grid(row=0, column=0, sticky="ns", ipadx=50, ipady=20)

    def item_count_clicked(self, event):
        logger.debug("Item count clicked")
        self.destroy()
        items = Item.read_all(self.session)
        ItemListFrame(
            self.parent,
            self.translations["items"]["item_list"],
            self.back_button_pressed,
            items,
        ).grid(row=0, column=0, sticky="ns", ipadx=50, ipady=20)

    def item_purchase_clicked(self, event):
        logger.debug("Item purchase clicked")
        self.destroy()
        items = Item.read_all(self.session)
        UserMainPage(self.parent, main_menu=self.main_menu, user=self.user, items=items)
