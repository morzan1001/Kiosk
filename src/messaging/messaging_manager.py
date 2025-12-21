"""Messaging manager that coordinates multiple messaging controllers."""

from typing import Dict, List, Optional

from src.logmgr import logger
from src.messaging.base_messaging_controller import BaseMessagingController


class MessagingManager:
    """
    Manager class for managing multiple message channels.
    Enables messages to be sent simultaneously via different channels.
    """

    def __init__(self):
        self.controllers: Dict[str, BaseMessagingController] = {}
        logger.debug("MessagingManager initialized")

    def add_controller(self, controller: BaseMessagingController, name: Optional[str] = None):
        """
        Adds a message channel controller.

        Args:
            controller: Instance of a BaseMessagingController
            name: Optional name for the controller (if not provided, channel_type is used)
        """
        controller_name = name or controller.get_channel_type()
        self.controllers[controller_name] = controller
        logger.info("Added messaging controller: %s", controller_name)

    def remove_controller(self, name: str):
        """
        Removes a message channel controller.

        Args:
            name: Name of the controller to remove
        """
        if name in self.controllers:
            controller = self.controllers[name]
            controller.stop()
            del self.controllers[name]
            logger.info("Removed messaging controller: %s", name)
        else:
            logger.warning("Controller %s not found", name)

    def get_controller(self, name: str) -> Optional[BaseMessagingController]:
        """
        Returns a specific controller.

        Args:
            name: Name of the controller

        Returns:
            Controller instance or None if not found
        """
        return self.controllers.get(name)

    def get_available_channels(self) -> List[str]:
        """
        Returns a list of all available message channels.

        Returns:
            List of available channel names
        """
        return list(self.controllers.keys())

    def send_message_to_all(self, recipient, message, subject=None, **kwargs):
        """
        Sends a message via all available channels.

        Args:
            recipient: Recipient of the message
            message: Message content
            subject: Subject (optional)
            **kwargs: Additional parameters
        """
        for name, controller in self.controllers.items():
            try:
                controller.send_message(recipient, message, subject, **kwargs)
                logger.debug("Message queued for %s", name)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Failed to queue message for %s", name)

    def send_message_to_channels(
        self, channels: List[str], recipient, message, subject=None, **kwargs
    ):
        """
        Sends a message via specific channels.

        Args:
            channels: List of channel names
            recipient: Recipient of the message
            message: Message content
            subject: Subject (optional)
            **kwargs: Additional parameters
        """
        for channel in channels:
            if channel in self.controllers:
                try:
                    self.controllers[channel].send_message(recipient, message, subject, **kwargs)
                    logger.debug("Message queued for %s", channel)
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.exception("Failed to queue message for %s", channel)
            else:
                logger.warning("Channel %s not available", channel)

    def notify_low_balance_all(self, recipient, balance, language="en"):
        """
        Sends low-balance notification via all channels.

        Args:
            recipient: Recipient of the notification
            balance: Current balance
            language: Language for the message
        """
        for name, controller in self.controllers.items():
            try:
                controller.notify_low_balance(recipient, balance, language)
                logger.debug("Low balance notification queued for %s", name)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Failed to queue low balance notification for %s", name)

    def notify_low_stock_all(self, recipient, product_name, available_quantity, language="en"):
        """
        Sends low-stock notification via all channels.

        Args:
            recipient: Recipient of the notification
            product_name: Name of the product
            available_quantity: Available quantity
            language: Language for the message
        """
        for name, controller in self.controllers.items():
            try:
                controller.notify_low_stock(recipient, product_name, available_quantity, language)
                logger.debug("Low stock notification queued for %s", name)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Failed to queue low stock notification for %s", name)

    def send_monthly_summary_all(self, recipient, summary, language="en"):
        """
        Sends monthly summary via all supported channels.

        Args:
            recipient: Recipient of the summary
            summary: Summary data
            language: Language for the message
        """
        for name, controller in self.controllers.items():
            try:
                controller.send_monthly_summary(recipient, summary, language)
                logger.debug("Monthly summary queued for %s", name)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Failed to queue monthly summary for %s", name)

    def stop_all(self):
        """Stops all controllers."""
        logger.info("Stopping all messaging controllers")
        for name, controller in self.controllers.items():
            try:
                controller.stop()
                logger.debug("Stopped controller: %s", name)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Failed to stop controller %s", name)

    def __enter__(self):
        """Enter the runtime context for the messaging manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and ensure cleanup."""
        self.stop_all()
        return False
