import threading
import queue
from abc import ABC, abstractmethod
from src.logmgr import logger
from src.localization.translator import get_translations


class BaseMessagingController(ABC):
    """
    Abstract base class for all message channels.
    Provides a uniform interface for different messaging services.
    """
    
    def __init__(self):
        """Initializes the common threading and queue components."""
        logger.debug(f"Initializing {self.__class__.__name__}")
        self.queue = queue.Queue()  
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._process_queue)
        self.thread.daemon = True
        self.thread.start()
        self.translations = get_translations()  
        
    def _process_queue(self):
        """Processes the message queue in a separate thread."""
        while not self._stop_event.is_set():
            try:
                task = self.queue.get(timeout=1)  # Timeout to regularly check if it should stop
                if task is None:
                    break
                self._execute_task(task)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"Failed to process message task in {self.__class__.__name__}: {str(e)}")
    
    def _execute_task(self, task):
        """Executes a specific task from the queue."""
        task_type = task.get('type')
        try:
            if task_type == 'send_message':
                self._send_message_internal(
                    recipient=task['recipient'],
                    subject=task.get('subject'),
                    message=task['message'],
                    **task.get('kwargs', {})
                )
            elif task_type == 'low_balance':
                self._notify_low_balance_internal(
                    recipient=task['recipient'],
                    balance=task['balance'],
                    language=task.get('language', 'de')  
                )
            elif task_type == 'low_stock':
                self._notify_low_stock_internal(
                    recipient=task['recipient'],
                    product_name=task['product_name'],
                    available_quantity=task['available_quantity'],
                    language=task.get('language', 'de') 
                )
            elif task_type == 'monthly_summary':
                self._send_monthly_summary_internal(
                    recipient=task['recipient'],
                    summary=task['summary'],
                    language=task.get('language', 'de')  
                )
            else:
                logger.warning(f"Unknown task type: {task_type}")
        except Exception as e:
            logger.error(f"Failed to execute task {task_type}: {str(e)}")
            
    # Public interface methods
    def send_message(self, recipient, message, subject=None, **kwargs):
        """
        Sends a general message.
        
        Args:
            recipient: Recipient of the message (email address, username, etc.)
            message: Message content
            subject: Subject (optional, relevant for email)
            **kwargs: Additional parameters depending on implementation
        """
        task = {
            'type': 'send_message',
            'recipient': recipient,
            'subject': subject,
            'message': message,
            'kwargs': kwargs
        }
        self.queue.put(task)
    
    def notify_low_balance(self, recipient, balance, language='en'):
        """
        Notifies about low balance.
        
        Args:
            recipient: Recipient of the notification
            balance: Current balance
            language: Language for the message
        """
        task = {
            'type': 'low_balance',
            'recipient': recipient,
            'balance': balance,
            'language': language
        }
        self.queue.put(task)
    
    def notify_low_stock(self, recipient, product_name, available_quantity, language='en'):
        """
        Notifies you when stock levels are low.
        
        Args:
            recipient: Recipient of the notification
            product_name: Name of the product
            available_quantity: Available quantity
            language: Language for the message
        """
        task = {
            'type': 'low_stock',
            'recipient': recipient,
            'product_name': product_name,
            'available_quantity': available_quantity,
            'language': language
        }
        self.queue.put(task)
    
    def send_monthly_summary(self, recipient, summary, language='en'):
        """
        Sends a monthly summary.

        Args:
            recipient: Recipient of the summary
            summary: Summary data
            language: Language for the message
        """
        task = {
            'type': 'monthly_summary',
            'recipient': recipient,
            'summary': summary,
            'language': language
        }
        self.queue.put(task)
    
    def stop(self):
        """Stops the message processing thread."""
        logger.debug(f"Stopping {self.__class__.__name__} thread")
        self._stop_event.set()
        self.queue.put(None)  # Signal to stop the queue processing
        if threading.current_thread() != self.thread:
            self.thread.join()

    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def _send_message_internal(self, recipient, message, subject=None, **kwargs):
        """
        Internal implementation for sending a message.
        Must be implemented by each subclass.
        """
        pass
    
    @abstractmethod
    def _notify_low_balance_internal(self, recipient, balance, language='en'):
        """
        Internal implementation for low-balance notifications.
        Must be implemented by each subclass.
        """
        pass
    
    @abstractmethod
    def _notify_low_stock_internal(self, recipient, product_name, available_quantity, language='en'):
        """
        Internal implementation for low-stock notifications.
        Must be implemented by each subclass.
        """
        pass
    
    def _send_monthly_summary_internal(self, recipient, summary, language='en'):
        """
        Internal implementation for sending monthly summaries.
        Standard implementation - can be overridden by subclasses.
        """
        logger.warning(f"{self.__class__.__name__} does not support monthly summaries")
    
    @abstractmethod
    def get_channel_type(self):
        """
        Returns the type of message channel (e.g., ‘email’, ‘mattermost’).
        Must be implemented by every subclass.
        """
        pass
