from src.ui.components.info_card_frame import InfoCardFrame


class ItemFrame(InfoCardFrame):
    def __init__(self, master, data, *args, **kwargs):
        item_image = data.image
        item_name = data.name
        item_price = data.price

        super().__init__(
            master,
            title=item_name,
            subtitle=f"{item_price:.2f}€",
            image_data=item_image,
            *args,
            **kwargs,
        )
