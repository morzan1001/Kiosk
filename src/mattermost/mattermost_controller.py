import requests
import threading
from queue import Queue
from src.logmgr import logger
from src.localization.translator import get_translations
from src.database.connection import get_db
from src.database.models.user import User

class MattermostController:
    def __init__(self, base_url, bot_token):
        self.base_url = base_url
        self.bot_token = bot_token
        self.queue = Queue()
        self.translations = get_translations()
        self.thread = threading.Thread(target=self._process_queue)
        self.thread.daemon = True
        self.thread.start()

    def send_public_message(self, channel_id, message):
        self.queue.put(("public", channel_id, message))

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

    def _send_public_message(self, channel_id, message):
        url = f"{self.base_url}/api/v4/posts"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel_id": channel_id,
            "message": message
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 201:
            logger.error(f"Failed to send public message to Mattermost: {response.text}")
        else:
            logger.info(f"Public message sent to Mattermost channel {channel_id}")

    def _send_direct_message(self, username: str, message: str):
        user_id = self._get_user_id(username)
        if not user_id:
            logger.error(f"Failed to find user ID for username: {username}")
            return

        url = f"{self.base_url}/api/v4/posts"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        # Create a direct message channel
        channel_url = f"{self.base_url}/api/v4/channels/direct"
        channel_payload = [user_id]
        channel_response = requests.post(channel_url, json=channel_payload, headers=headers)
        if channel_response.status_code != 201:
            logger.error(f"Failed to create direct message channel: {channel_response.text}")
            return
        channel_id = channel_response.json()["id"]

        # Send the message
        payload = {
            "channel_id": channel_id,
            "message": message
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 201:
            logger.error(f"Failed to send direct message to Mattermost user {user_id}: {response.text}")
        else:
            logger.info(f"Direct message sent to Mattermost user {user_id}")


    def _get_user_id(self, username: str):
        url = f"{self.base_url}/api/v4/users/username/{username}"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get user ID for username {username}: {response.text}")
            return None
        return response.json().get("id")

    def notify_low_balance(self, user, balance):
        """Notify user about low balance via Mattermost."""
        translations = get_translations()
        if user.mattermost_user_id and user.notifications_enabled:
            message = translations["mattermost"]["low_balance"].format(name=user.name, balance=balance)
            self.send_direct_message(
                user_id=user.mattermost_user_id,
                message=message
            )
            logger.info(f"Low balance notification sent to user {user.name} ({user.mattermost_user_id})")
        else:
            logger.warning(f"User {user.name} does not have a Mattermost user ID or notifications are disabled, skipping low balance notification.")

    def notify_low_stock(self, admin, product_name, available_quantity):
        """Notify admin about low stock via Mattermost."""
        translations = get_translations()
        if admin.mattermost_user_id and admin.notifications_enabled:
            message = translations["mattermost"]["low_stock"].format(product_name=product_name, available_quantity=available_quantity)
            self.send_direct_message(
                user_id=admin.mattermost_user_id,
                message=message
            )
            logger.info(f"Low stock notification sent to admin {admin.name} ({admin.mattermost_user_id})")
        else:
            logger.warning(f"Admin {admin.name} does not have a Mattermost user ID or notifications are disabled, skipping low stock notification.")
