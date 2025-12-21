"""
Base Messaging Controller Module.
Provides an abstract base class for all messaging channels.
"""

import queue
import threading
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from src.localization.translator import get_translations
from src.logmgr import logger


class BaseMessagingController(ABC):
    """
    Abstract base class for all message channels.
    Provides a uniform interface for different messaging services.
    """

    def __init__(self) -> None:
        """Initializes the common threading and queue components."""
        logger.debug("Initializing %s", self.__class__.__name__)
        self.queue: queue.Queue[Optional[Dict[str, Any]]] = queue.Queue()
        self._stop_event: threading.Event = threading.Event()
        self.thread: threading.Thread = threading.Thread(target=self._process_queue)
        self.thread.daemon = True
        self.thread.start()
        self.translations: Dict[str, Any] = get_translations()

    def _process_queue(self) -> None:
        """Processes the message queue in a separate thread."""
        while not self._stop_event.is_set():
            try:
                task: Optional[Dict[str, Any]] = self.queue.get(timeout=1)
                if task is None:
                    break
                self._execute_task(task)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception:  # pylint: disable=broad-exception-caught
                if not self._stop_event.is_set():
                    logger.exception(
                        "Failed to process message task in %s",
                        self.__class__.__name__,
                    )

    def _execute_task(self, task: Dict[str, Any]) -> None:
        """
        Executes a specific task from the queue.

        Args:
            task: Dictionary containing task type and parameters.
        """
        task_type: Optional[str] = task.get("type")
        try:
            if task_type == "send_message":
                self._send_message_internal(
                    recipient=task["recipient"],
                    subject=task.get("subject"),
                    message=task["message"],
                    **task.get("kwargs", {}),
                )
            elif task_type == "low_balance":
                self._notify_low_balance_internal(
                    recipient=task["recipient"],
                    balance=task["balance"],
                    language=task.get("language", "en"),
                )
            elif task_type == "low_stock":
                self._notify_low_stock_internal(
                    recipient=task["recipient"],
                    product_name=task["product_name"],
                    available_quantity=task["available_quantity"],
                    language=task.get("language", "en"),
                )
            elif task_type == "monthly_summary":
                self._send_monthly_summary_internal(
                    recipient=task["recipient"],
                    summary=task["summary"],
                    language=task.get("language", "en"),
                )
            else:
                logger.warning("Unknown task type: %s", task_type)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Failed to execute task %s", task_type)

    def send_message(
        self, recipient: str, message: str, subject: Optional[str] = None, **kwargs: Any
    ) -> None:
        """
        Sends a general message.

        Args:
            recipient: Recipient of the message (email address, username, etc.)
            message: Message content
            subject: Subject (optional, relevant for email)
            **kwargs: Additional parameters depending on implementation
        """
        task: Dict[str, Any] = {
            "type": "send_message",
            "recipient": recipient,
            "subject": subject,
            "message": message,
            "kwargs": kwargs,
        }
        self.queue.put(task)

    def notify_low_balance(
        self, recipient: Union[str, Any], balance: float, language: str = "en"
    ) -> None:
        """
        Notifies about low balance.

        Args:
            recipient: Recipient of the notification
            balance: Current balance
            language: Language for the message
        """
        task: Dict[str, Any] = {
            "type": "low_balance",
            "recipient": recipient,
            "balance": balance,
            "language": language,
        }
        self.queue.put(task)

    def notify_low_stock(
        self,
        recipient: Union[str, Any],
        product_name: str,
        available_quantity: int,
        language: str = "en",
    ) -> None:
        """
        Notifies you when stock levels are low.

        Args:
            recipient: Recipient of the notification
            product_name: Name of the product
            available_quantity: Available quantity
            language: Language for the message
        """
        task: Dict[str, Any] = {
            "type": "low_stock",
            "recipient": recipient,
            "product_name": product_name,
            "available_quantity": available_quantity,
            "language": language,
        }
        self.queue.put(task)

    def send_monthly_summary(self, recipient: str, summary: Any, language: str = "en") -> None:
        """
        Sends a monthly summary.

        Args:
            recipient: Recipient of the summary
            summary: Summary data
            language: Language for the message
        """
        task: Dict[str, Any] = {
            "type": "monthly_summary",
            "recipient": recipient,
            "summary": summary,
            "language": language,
        }
        self.queue.put(task)

    def stop(self) -> None:
        """Stops the message processing thread."""
        logger.debug("Stopping %s thread", self.__class__.__name__)
        self._stop_event.set()
        self.queue.put(None)
        if threading.current_thread() != self.thread:
            self.thread.join()

    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def _send_message_internal(
        self, recipient: str, message: str, subject: Optional[str] = None, **kwargs: Any
    ) -> None:
        """
        Internal implementation for sending a message.
        Must be implemented by each subclass.
        """

    @abstractmethod
    def _notify_low_balance_internal(
        self, recipient: Union[str, Any], balance: float, language: str = "en"
    ) -> None:
        """
        Internal implementation for low-balance notifications.
        Must be implemented by each subclass.
        """

    @abstractmethod
    def _notify_low_stock_internal(
        self,
        recipient: Union[str, Any],
        product_name: str,
        available_quantity: int,
        language: str = "en",
    ) -> None:
        """
        Internal implementation for low-stock notifications.
        Must be implemented by each subclass.
        """

    def _send_monthly_summary_internal(
        self, recipient: str, summary: Any, language: str = "en"
    ) -> None:
        """
        Internal implementation for sending monthly summaries.
        Standard implementation - can be overridden by subclasses.
        """
        # pylint: disable=unused-argument
        logger.warning(
            "%s does not support monthly summaries",
            self.__class__.__name__,
        )

    @abstractmethod
    def get_channel_type(self) -> str:
        """
        Returns the type of message channel (e.g., ‘email’, ‘mattermost’).
        Must be implemented by every subclass.
        """
        raise NotImplementedError
