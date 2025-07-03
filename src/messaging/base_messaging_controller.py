from abc import ABC, abstractmethod
import threading
from queue import Queue
from src.logmgr import logger


class BaseMessagingController(ABC):
    """
    Abstrakte Basisklasse für alle Nachrichtenkanäle.
    Stellt ein einheitliches Interface für verschiedene Messaging-Services bereit.
    """
    
    def __init__(self):
        """Initialisiert die gemeinsamen Threading- und Queue-Komponenten."""
        logger.debug(f"Initializing {self.__class__.__name__}")
        self.queue = Queue()
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._process_queue)
        self.thread.daemon = True
        self.thread.start()
        
    def _process_queue(self):
        """Verarbeitet die Nachrichten-Queue in einem separaten Thread."""
        while not self._stop_event.is_set():
            try:
                task = self.queue.get(timeout=1)  # Timeout um regelmäßig zu prüfen ob gestoppt werden soll
                if task is None:
                    break
                self._execute_task(task)
                self.queue.task_done()
            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"Failed to process message task in {self.__class__.__name__}: {e}")
    
    def _execute_task(self, task):
        """Führt eine spezifische Aufgabe aus der Queue aus."""
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
                    language=task.get('language', 'en')
                )
            elif task_type == 'low_stock':
                self._notify_low_stock_internal(
                    recipient=task['recipient'],
                    product_name=task['product_name'],
                    available_quantity=task['available_quantity'],
                    language=task.get('language', 'en')
                )
            elif task_type == 'monthly_summary':
                self._send_monthly_summary_internal(
                    recipient=task['recipient'],
                    summary=task['summary'],
                    language=task.get('language', 'en')
                )
            else:
                logger.warning(f"Unknown task type: {task_type}")
        except Exception as e:
            logger.error(f"Failed to execute task {task_type}: {e}")
    
    # Öffentliche Interface-Methoden
    def send_message(self, recipient, message, subject=None, **kwargs):
        """
        Sendet eine allgemeine Nachricht.
        
        Args:
            recipient: Empfänger der Nachricht (Email-Adresse, Username, etc.)
            message: Nachrichteninhalt
            subject: Betreff (optional, für Email relevant)
            **kwargs: Zusätzliche Parameter je nach Implementation
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
        Benachrichtigt über niedrigen Kontostand.
        
        Args:
            recipient: Empfänger der Benachrichtigung
            balance: Aktueller Kontostand
            language: Sprache für die Nachricht
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
        Benachrichtigt über niedrigen Lagerbestand.
        
        Args:
            recipient: Empfänger der Benachrichtigung
            product_name: Name des Produkts
            available_quantity: Verfügbare Menge
            language: Sprache für die Nachricht
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
        Sendet eine monatliche Zusammenfassung.
        
        Args:
            recipient: Empfänger der Zusammenfassung
            summary: Zusammenfassungsdaten
            language: Sprache für die Nachricht
        """
        task = {
            'type': 'monthly_summary',
            'recipient': recipient,
            'summary': summary,
            'language': language
        }
        self.queue.put(task)
    
    def stop(self):
        """Stoppt den Message-Verarbeitungsthread."""
        logger.debug(f"Stopping {self.__class__.__name__} thread")
        self._stop_event.set()
        self.queue.put(None)  # Signal zum Beenden der Queue-Verarbeitung
        if threading.current_thread() != self.thread:
            self.thread.join()
    
    # Abstrakte Methoden, die von Subklassen implementiert werden müssen
    @abstractmethod
    def _send_message_internal(self, recipient, message, subject=None, **kwargs):
        """
        Interne Implementierung zum Senden einer Nachricht.
        Muss von jeder Subklasse implementiert werden.
        """
        pass
    
    @abstractmethod
    def _notify_low_balance_internal(self, recipient, balance, language='en'):
        """
        Interne Implementierung für Low-Balance-Benachrichtigungen.
        Muss von jeder Subklasse implementiert werden.
        """
        pass
    
    @abstractmethod
    def _notify_low_stock_internal(self, recipient, product_name, available_quantity, language='en'):
        """
        Interne Implementierung für Low-Stock-Benachrichtigungen.
        Muss von jeder Subklasse implementiert werden.
        """
        pass
    
    def _send_monthly_summary_internal(self, recipient, summary, language='en'):
        """
        Interne Implementierung für monatliche Zusammenfassungen.
        Standard-Implementation - kann von Subklassen überschrieben werden.
        """
        logger.warning(f"{self.__class__.__name__} does not support monthly summaries")
    
    @abstractmethod
    def get_channel_type(self):
        """
        Gibt den Typ des Nachrichtenkanals zurück (z.B. 'email', 'mattermost').
        Muss von jeder Subklasse implementiert werden.
        """
        pass
