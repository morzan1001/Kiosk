import requests
import threading
from queue import Queue
from src.logmgr import logger
from src.localization.translator import get_translations

class MattermostController:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.queue = Queue()
        self.translations = get_translations()
        self.thread = threading.Thread(target=self._process_queue)
        self.thread.daemon = True
        self.thread.start()

    def send_public_message(self, channel, message):
        self.queue.put(("public", channel, message))

    def send_direct_message(self, username, message):
        self.queue.put(("direct", username, message))

    def _process_queue(self):
        while True:
            message_type, target, message = self.queue.get()
            try:
                if message_type == "public":
                    self._send_public_message(target, message)
                elif message_type == "direct":
                    self._send_direct_message(target, message)
                self.queue.task_done()
            except Exception as e:
                logger.error(f"Failed to process Mattermost message task: {e}")

    def _send_public_message(self, channel, message):
        payload = {
            "channel": channel,
            "username": self.translations["general"]["kiosk_title"],
            "icon_emoji": ":bell:",
            "text": message
        }
        response = requests.post(self.webhook_url, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to send public message to Mattermost: {response.text}")
        else:
            logger.info(f"Public message sent to Mattermost channel {channel}")

    def _send_direct_message(self, username, message):
        payload = {
            "channel": f"@{username}",
            "username": self.translations["general"]["kiosk_title"],
            "icon_emoji": ":bell:",
            "text": message
        }
        response = requests.post(self.webhook_url, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to send direct message to Mattermost user {username}: {response.text}")
        else:
            logger.info(f"Direct message sent to Mattermost user {username}")
    
    def notify_low_balance(self, user, balance):
        """Notify user about low balance via Mattermost."""
        message = self.translations["mattermost"]["low_balance"].format(name=user.name, balance=balance)
        self.send_direct_message(
            username=user.mattermost_username,
            message=message
        )
        logger.info(f"Low balance notification sent to user {user.name} ({user.mattermost_username})")
    
    def notify_low_stock(self, admin, product_name, available_quantity):
        """Notify admin about low stock via Mattermost."""
        message = self.translations["mattermost"]["low_stock"].format(product_name=product_name, available_quantity=available_quantity)
        self.send_direct_message(
            username=admin.mattermost_username,
            message=message
        )
        logger.info(f"Low stock notification sent to admin {admin.name} ({admin.mattermost_username})")