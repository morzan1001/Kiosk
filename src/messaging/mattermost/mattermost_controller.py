"""Mattermost messaging controller implementation."""

import requests

from src.localization.translator import get_translations
from src.logmgr import logger
from src.messaging.base_messaging_controller import BaseMessagingController


class MattermostController(BaseMessagingController):
    """Controller for Mattermost messages based on the standardized messaging interface."""

    TIMEOUT = 10

    def __init__(self, base_url, bot_token):
        self.base_url = base_url
        self.bot_token = bot_token
        self.translations = get_translations()

        # Initialize the base class (threading and queue)
        super().__init__()

    def _get_headers(self):
        """Returns the standard headers for Mattermost API requests."""
        return {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json",
        }

    def get_channel_type(self):
        """Returns the message channel type."""
        return "mattermost"

    def _send_message_internal(self, recipient, message, subject=None, **kwargs):
        """
        Internal implementation for sending a Mattermost message.

        Args:
            recipient: Username or channel ID
            message: Message content
            subject: Ignored by Mattermost (no subject concept)
            **kwargs: Can contain ‘channel_id’ for public messages
        """
        channel_id = kwargs.get("channel_id")

        if channel_id:
            # Public message to channel
            self._send_public_message(channel_id, message)
        else:
            # Direct message to user
            self._send_direct_message(recipient, message)

    def _notify_low_balance_internal(self, recipient, balance, language="en"):
        """Internal implementation for low-balance notifications."""
        try:
            # Ensure balance is a float for formatting
            balance_float = float(balance) if not isinstance(balance, float) else balance

            # Use the system translations (ignore language parameter)
            message = self.translations["mattermost"]["low_balance"].format(
                name=getattr(recipient, "name", str(recipient)), balance=balance_float
            )
        except (KeyError, ValueError, AttributeError) as e:
            logger.error("Error accessing translations: %s", e)
            # Fallback message
            message = f"Your credit balance is low: {float(balance):.2f}€"

        # If recipient is a User object, use mattermost_username
        username = getattr(recipient, "mattermost_username", recipient)
        if username:
            self._send_direct_message(username, message)
            logger.info("Low balance notification sent via Mattermost to %s", username)
        else:
            logger.warning("No Mattermost username available for recipient %s", recipient)

    def _notify_low_stock_internal(
        self, recipient, product_name, available_quantity, language="en"
    ):
        """Internal implementation for low-stock notifications."""
        try:
            # Use the system translations (ignore language parameter)
            message = self.translations["mattermost"]["low_stock"].format(
                product_name=product_name, available_quantity=available_quantity
            )
        except (KeyError, ValueError) as e:
            logger.error("Error accessing translations: %s", e)
            # Fallback message
            message = f"Low stock levels: {product_name} - only {available_quantity} available"

        # If recipient is a User object, use mattermost_username
        username = getattr(recipient, "mattermost_username", recipient)
        if username:
            self._send_direct_message(username, message)
            logger.info("Low stock notification sent via Mattermost to %s", username)
        else:
            logger.warning("No Mattermost username available for recipient %s", recipient)

    def _send_public_message(self, channel_id, message):
        """Sends a public message to a Mattermost channel."""
        url = f"{self.base_url}/api/v4/posts"
        headers = self._get_headers()
        payload = {"channel_id": channel_id, "message": message}
        response = requests.post(url, json=payload, headers=headers, timeout=self.TIMEOUT)
        if response.status_code != 201:
            logger.error("Failed to send public message to Mattermost: %s", response.text)
        else:
            logger.info("Public message sent to Mattermost channel %s", channel_id)

    def _send_direct_message(self, username: str, message: str):
        """Sends a direct message to a Mattermost user."""
        user_id = self._get_user_id(username)
        if not user_id:
            logger.error("Failed to find user ID for username: %s", username)
            return

        url = f"{self.base_url}/api/v4/posts"
        headers = self._get_headers()
        # Create a direct message channel
        channel_url = f"{self.base_url}/api/v4/channels/direct"
        channel_payload = [self._get_bot_user_id(), user_id]
        channel_response = requests.post(
            channel_url, json=channel_payload, headers=headers, timeout=self.TIMEOUT
        )
        if channel_response.status_code != 201:
            logger.error("Failed to create direct message channel: %s", channel_response.text)
            return
        channel_id = channel_response.json()["id"]

        # Send the message
        payload = {"channel_id": channel_id, "message": message}
        response = requests.post(url, json=payload, headers=headers, timeout=self.TIMEOUT)
        if response.status_code != 201:
            logger.error(
                "Failed to send direct message to Mattermost user %s: %s",
                user_id,
                response.text,
            )
        else:
            logger.info("Direct message sent to Mattermost user %s", user_id)

    def _get_user_id(self, username: str):
        """Retrieves the user ID for a given username."""
        # Remove the '@' symbol if present
        if username.startswith("@"):
            username = username[1:]

        url = f"{self.base_url}/api/v4/users/username/{username}"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if response.status_code != 200:
            logger.error("Failed to get user ID for username %s: %s", username, response.text)
            return None
        return response.json().get("id")

    def _get_bot_user_id(self):
        """Returns the bot user's ID."""
        url = f"{self.base_url}/api/v4/users/me"
        headers = self._get_headers()
        response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if response.status_code != 200:
            logger.error("Failed to get bot user ID: %s", response.text)
            return None
        return response.json().get("id")
