from src.localization.translator import get_translations
from src.ui.components.info_card_frame import InfoCardFrame
from src.utils.paths import get_image_path


class UserFrame(InfoCardFrame):
    def __init__(self, master, data, *args, **kwargs):
        user_id, user_name, user_credit = data
        self.translations = get_translations()

        super().__init__(
            master,
            title=user_name,
            subtitle=self.translations["user"]["credit_balance"].format(
                user_credit=user_credit
            ),
            image_path=get_image_path("user-big.png"),
            *args,
            **kwargs
        )
