import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from src.logmgr import logger
from src.localization.translator import get_translations
from jinja2 import Environment, FileSystemLoader
import os
import threading
from queue import Queue

class EmailController:
    """Manages email notifications by sending dynamic, template-based emails via SMTP."""
    
    def __init__(self, smtp_server, smtp_port, login, password):
        logger.debug("Initializing EmailController with SMTP server details")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.login = login
        self.password = password
        self.translations = get_translations()
        logger.debug("Translations loaded")

        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        logger.debug("Jinja2 environment set up")

        # Set up threading and queue
        self.queue = Queue()
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._process_queue)
        self.thread.start()
    
    def _process_queue(self):
        while not self._stop_event.is_set():
            try:
                task = self.queue.get()  # Blocks until an item is available
                if task is None:
                    break
                self._send_email(*task)
                self.queue.task_done()
            except Exception as e:
                logger.error(f"Failed to process email task: {e}")

    def send_email(self, recipient_email, subject, body, is_html=False):
        logger.debug(f"Queueing email to {recipient_email} with subject '{subject}'")
        self.queue.put((recipient_email, subject, body, is_html))
    
    def _send_email(self, recipient_email, subject, body, is_html):
        try:
            logger.debug(f"Sending email to {recipient_email} with subject '{subject}'")
            msg = MIMEMultipart('related')
            msg['From'] = self.login
            msg['To'] = recipient_email
            msg['Subject'] = subject

            body_part = MIMEText(body, 'html' if is_html else 'plain', 'utf-8')
            msg.attach(body_part)
            logger.debug("Email body attached")

            # Add logo as inline image
            try:
                logger.debug("Adding logo as inline image")
                logo_path = os.path.join(os.path.dirname(__file__), 'assets/logo.png')
                with open(logo_path, 'rb') as img_file:
                    img_data = img_file.read()
                image = MIMEImage(img_data, name='logo.png')
                image.add_header('Content-ID', '<logo>')
                msg.attach(image)
            except Exception as e:
                logger.warning(f"Failed to attach logo image: {e}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.login, self.password)
                server.send_message(msg)

            logger.info(f"Email sent to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def load_template(self, template_name, context):
        try:
            logger.debug(f"Loading email template '{template_name}'")
            footer_text = self.translations['email']['footer']
            current_date = datetime.now().strftime('%d.%m.%Y')

            context.update({
                'do_not_respond': self.translations['email']['do_not_respond'],
                'footer': f"{footer_text} - {current_date}",
            })

            template = self.jinja_env.get_template(template_name)
            full_body = template.render(context)
            logger.debug("Email body rendered using Jinja2")
            return full_body
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return ""

    def notify_low_balance(self, recipient_email, balance, language='en'):
        translated_subject = self.translations["email"]["low_balance_subject"]
        template_file = f"low_balance_{language}.html"
        body = self.load_template(template_file, {"balance": balance})
        self.send_email(recipient_email, translated_subject, body, is_html=True)

    def send_monthly_summary(self, recipient_email, summary, language='en'):
        translated_subject = self.translations["email"]["monthly_summary_subject"]
        template_file = f"monthly_summary_{language}.html"
        body = self.load_template(template_file, {"summary": summary})
        self.send_email(recipient_email, translated_subject, body, is_html=True)

    def notify_low_stock(self, recipient_email, product_name, available_quantity, language='en', subject=None):
        translated_subject = subject or self.translations["email"]["low_stock_subject"]
        template_file = f"product_low_stock_{language}.html"
        body = self.load_template(template_file, {"product_name": product_name, "available_quantity": available_quantity})
        self.send_email(recipient_email, translated_subject, body, is_html=True)

    def stop(self):
        logger.debug("Stopping email sender thread")
        self._stop_event.set()
        self.queue.put(None)  # To unblock the queue if it's waiting
        if threading.current_thread() != self.thread:
            self.thread.join()