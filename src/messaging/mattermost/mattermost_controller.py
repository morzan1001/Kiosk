import requests
from src.logmgr import logger
from src.localization.translator import get_translations
from src.messaging.base_messaging_controller import BaseMessagingController


class MattermostController(BaseMessagingController):
    """Controller for Mattermost messages based on the standardized messaging interface."""
    
    def __init__(self, base_url, bot_token):
        self.base_url = base_url
        self.bot_token = bot_token
        self.translations = get_translations()
        
        # Initialisiere die Basisklasse (Threading und Queue)
        super().__init__()
    
    def get_channel_type(self):
        """Gibt den Nachrichtenkanal-Typ zurück."""
        return 'mattermost'
    
    def _send_message_internal(self, recipient, message, subject=None, **kwargs):
        """
        Interne Implementierung zum Senden einer Mattermost-Nachricht.
        
        Args:
            recipient: Username oder Channel-ID
            message: Nachrichteninhalt
            subject: Wird bei Mattermost ignoriert (kein Betreff-Konzept)
            **kwargs: Kann 'channel_id' enthalten für Public-Messages
        """
        channel_id = kwargs.get('channel_id')
        
        if channel_id:
            # Public message to channel
            self._send_public_message(channel_id, message)
        else:
            # Direct message to user
            self._send_direct_message(recipient, message)
    
    def _notify_low_balance_internal(self, recipient, balance, language='en'):
        """Interne Implementierung für Low-Balance-Benachrichtigungen."""
        message = self.translations["mattermost"]["low_balance"].format(
            name=getattr(recipient, 'name', str(recipient)), 
            balance=balance
        )
        
        # Wenn recipient ein User-Objekt ist, verwende mattermost_username
        username = getattr(recipient, 'mattermost_username', recipient)
        if username:
            self._send_direct_message(username, message)
            logger.info(f"Low balance notification sent via Mattermost to {username}")
        else:
            logger.warning(f"No Mattermost username available for recipient {recipient}")
    
    def _notify_low_stock_internal(self, recipient, product_name, available_quantity, language='en'):
        """Interne Implementierung für Low-Stock-Benachrichtigungen."""
        message = self.translations["mattermost"]["low_stock"].format(
            product_name=product_name, 
            available_quantity=available_quantity
        )
        
        # Wenn recipient ein User-Objekt ist, verwende mattermost_username
        username = getattr(recipient, 'mattermost_username', recipient)
        if username:
            self._send_direct_message(username, message)
            logger.info(f"Low stock notification sent via Mattermost to {username}")
        else:
            logger.warning(f"No Mattermost username available for recipient {recipient}")
    
    def _send_public_message(self, channel_id, message):
        """Sendet eine öffentliche Nachricht an einen Mattermost-Channel."""
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
        """Sendet eine direkte Nachricht an einen Mattermost-User."""
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
        channel_payload = [self._get_bot_user_id(), user_id]
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
        """Ermittelt die User-ID für einen gegebenen Username."""
        # Entferne das '@'-Symbol, falls vorhanden
        if username.startswith('@'):
            username = username[1:]

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

    def _get_bot_user_id(self):
        """Ermittelt die User-ID des Bots."""
        url = f"{self.base_url}/api/v4/users/me"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get bot user ID: {response.text}")
            return None
        return response.json().get("id")
