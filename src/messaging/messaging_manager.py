from typing import List, Dict, Optional
from src.logmgr import logger
from src.messaging.base_messaging_controller import BaseMessagingController


class MessagingManager:
    """
    Manager-Klasse zur Verwaltung mehrerer Nachrichtenkanäle.
    Ermöglicht das gleichzeitige Versenden von Nachrichten über verschiedene Kanäle.
    """
    
    def __init__(self):
        self.controllers: Dict[str, BaseMessagingController] = {}
        logger.debug("MessagingManager initialized")
    
    def add_controller(self, controller: BaseMessagingController, name: Optional[str] = None):
        """
        Fügt einen Nachrichtenkanal-Controller hinzu.
        
        Args:
            controller: Instance eines BaseMessagingController
            name: Optionaler Name für den Controller (falls nicht angegeben, wird channel_type verwendet)
        """
        controller_name = name or controller.get_channel_type()
        self.controllers[controller_name] = controller
        logger.info(f"Added messaging controller: {controller_name}")
    
    def remove_controller(self, name: str):
        """
        Entfernt einen Nachrichtenkanal-Controller.
        
        Args:
            name: Name des zu entfernenden Controllers
        """
        if name in self.controllers:
            controller = self.controllers[name]
            controller.stop()
            del self.controllers[name]
            logger.info(f"Removed messaging controller: {name}")
        else:
            logger.warning(f"Controller {name} not found")
    
    def get_controller(self, name: str) -> Optional[BaseMessagingController]:
        """
        Gibt einen spezifischen Controller zurück.
        
        Args:
            name: Name des Controllers
            
        Returns:
            Controller-Instance oder None falls nicht gefunden
        """
        return self.controllers.get(name)
    
    def get_available_channels(self) -> List[str]:
        """
        Gibt eine Liste aller verfügbaren Nachrichtenkanäle zurück.
        
        Returns:
            Liste der verfügbaren Kanal-Namen
        """
        return list(self.controllers.keys())
    
    def send_message_to_all(self, recipient, message, subject=None, **kwargs):
        """
        Sendet eine Nachricht über alle verfügbaren Kanäle.
        
        Args:
            recipient: Empfänger der Nachricht
            message: Nachrichteninhalt
            subject: Betreff (optional)
            **kwargs: Zusätzliche Parameter
        """
        for name, controller in self.controllers.items():
            try:
                controller.send_message(recipient, message, subject, **kwargs)
                logger.debug(f"Message queued for {name}")
            except Exception as e:
                logger.error(f"Failed to queue message for {name}: {e}")
    
    def send_message_to_channels(self, channels: List[str], recipient, message, subject=None, **kwargs):
        """
        Sendet eine Nachricht über spezifische Kanäle.
        
        Args:
            channels: Liste der Kanal-Namen
            recipient: Empfänger der Nachricht
            message: Nachrichteninhalt
            subject: Betreff (optional)
            **kwargs: Zusätzliche Parameter
        """
        for channel in channels:
            if channel in self.controllers:
                try:
                    self.controllers[channel].send_message(recipient, message, subject, **kwargs)
                    logger.debug(f"Message queued for {channel}")
                except Exception as e:
                    logger.error(f"Failed to queue message for {channel}: {e}")
            else:
                logger.warning(f"Channel {channel} not available")
    
    def notify_low_balance_all(self, recipient, balance, language='en'):
        """
        Sendet Low-Balance-Benachrichtigung über alle Kanäle.
        
        Args:
            recipient: Empfänger der Benachrichtigung
            balance: Aktueller Kontostand
            language: Sprache für die Nachricht
        """
        for name, controller in self.controllers.items():
            try:
                controller.notify_low_balance(recipient, balance, language)
                logger.debug(f"Low balance notification queued for {name}")
            except Exception as e:
                logger.error(f"Failed to queue low balance notification for {name}: {e}")
    
    def notify_low_stock_all(self, recipient, product_name, available_quantity, language='en'):
        """
        Sendet Low-Stock-Benachrichtigung über alle Kanäle.
        
        Args:
            recipient: Empfänger der Benachrichtigung
            product_name: Name des Produkts
            available_quantity: Verfügbare Menge
            language: Sprache für die Nachricht
        """
        for name, controller in self.controllers.items():
            try:
                controller.notify_low_stock(recipient, product_name, available_quantity, language)
                logger.debug(f"Low stock notification queued for {name}")
            except Exception as e:
                logger.error(f"Failed to queue low stock notification for {name}: {e}")
    
    def send_monthly_summary_all(self, recipient, summary, language='en'):
        """
        Sendet monatliche Zusammenfassung über alle unterstützten Kanäle.
        
        Args:
            recipient: Empfänger der Zusammenfassung
            summary: Zusammenfassungsdaten
            language: Sprache für die Nachricht
        """
        for name, controller in self.controllers.items():
            try:
                controller.send_monthly_summary(recipient, summary, language)
                logger.debug(f"Monthly summary queued for {name}")
            except Exception as e:
                logger.error(f"Failed to queue monthly summary for {name}: {e}")
    
    def stop_all(self):
        """Stoppt alle Controller."""
        logger.info("Stopping all messaging controllers")
        for name, controller in self.controllers.items():
            try:
                controller.stop()
                logger.debug(f"Stopped controller: {name}")
            except Exception as e:
                logger.error(f"Failed to stop controller {name}: {e}")
    
    def __del__(self):
        """Cleanup beim Zerstören des Managers."""
        self.stop_all()
