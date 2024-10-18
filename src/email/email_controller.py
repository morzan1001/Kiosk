import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from src.logmgr import logger
from src.localization.translator import get_translations
import os

class EmailController:
    """Manages email notifications by sending dynamic, template-based emails via SMTP."""
    def __init__(self, smtp_server, smtp_port, login, password):
        # Initialize the EmailController with SMTP server details and load translations
        logger.debug("Initializing EmailController with SMTP server details")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.login = login
        self.password = password
        self.translations = get_translations()
        logger.debug("Translations loaded")

    def send_email(self, recipient_email, subject, body, is_html=False):
        # Sends an email with the provided subject and body to the recipient_email
        try:
            logger.debug(f"Preparing to send email to {recipient_email} with subject '{subject}'")
            msg = MIMEMultipart()
            msg['From'] = self.login
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Attach the body text, which can be plain or HTML
            body_part = MIMEText(body, 'html' if is_html else 'plain')
            msg.attach(body_part)
            logger.debug("Email body attached")

            # Add logo as inline image in the email
            logger.debug("Adding logo as inline image")
            logo_path = os.path.join(os.path.dirname(__file__), '../../assets/logo.png')
            with open(logo_path, 'rb') as img_file:
                img_data = img_file.read()
            image = MIMEImage(img_data, name='logo.png')
            image.add_header('Content-ID', '<logo>')
            msg.attach(image)

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                logger.debug("Connecting to SMTP server")
                server.starttls()
                server.login(self.login, self.password)
                logger.debug("Logged in to SMTP server")
                server.send_message(msg)

            logger.info(f"Email sent to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def load_template(self, template_name, context):
        # Loads an email template, fills it with the provided context, and returns the full email body
        try:
            logger.debug(f"Loading email template '{template_name}'")
            template_path = os.path.join(os.path.dirname(__file__), 'templates', template_name)
            with open(template_path, 'r', encoding='utf-8') as file:
                content_template = file.read()

            base_template_path = os.path.join(os.path.dirname(__file__), 'templates', 'base.html')
            with open(base_template_path, 'r', encoding='utf-8') as base_file:
                base_template = base_file.read()

            logger.debug("Email template and base template loaded")
            
            # Prepare the footer with translation and current date
            footer_text = self.translations["email"]["footer"]
            current_date = datetime.now().strftime("%d.%m.%Y")
            footer_with_date = f"{footer_text} - {current_date}"
            logger.debug(f"Footer prepared with current date: {footer_with_date}")

            do_not_respond = self.translations["email"]["do_not_respond"]

            content = content_template.format(**context)
            full_body = base_template.replace("{{ content }}", content).replace("{{ do_not_respond }}", do_not_respond).replace("{{ footer }}", footer_with_date)
            logger.debug("Full email body constructed")
            return full_body
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return ""

    def notify_low_balance(self, recipient_email, balance, language='en'):
        # Sends a low balance notification email to the user
        translated_subject = self.translations["email"]["low_balance_subject"]
        template_file = f"low_balance_{language}.html"
        body = self.load_template(template_file, {"balance": balance})
        self.send_email(recipient_email, translated_subject, body, is_html=True)

    def send_monthly_summary(self, recipient_email, summary, language='en'):
        # Sends a monthly summary email to the user
        translated_subject = self.translations["email"]["monthly_summary_subject"]
        template_file = f"monthly_summary_{language}.html"
        body = self.load_template(template_file, {"summary": summary})
        self.send_email(recipient_email, translated_subject, body, is_html=True)

    def notify_low_stock(self, recipient_email, product_name, available_quantity, language='en'):
        # Sends a low stock notification email to the user
        translated_subject = self.translations["email"]["low_stock_subject"]
        template_file = f"product_low_stock_{language}.html"
        body = self.load_template(template_file, {"product_name": product_name, "available_quantity": available_quantity})
        self.send_email(recipient_email, translated_subject, body, is_html=True)