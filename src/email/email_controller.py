import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from src.logmgr import logger
from src.localization.translator import get_translations
from jinja2 import Environment, FileSystemLoader
import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from src.logmgr import logger
from src.localization.translator import get_translations
from jinja2 import Environment, FileSystemLoader
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

        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        logger.debug("Jinja2 environment set up")

    def send_email(self, recipient_email, subject, body, is_html=False):
        # Sends an email with the provided subject and body to the recipient_email
        try:
            logger.debug(f"Preparing to send email to {recipient_email} with subject '{subject}'")
            msg = MIMEMultipart('related')
            msg['From'] = self.login
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Attach the body text, which should be HTML in this case
            body_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(body_part)
            logger.debug("Email body attached")

            # Add logo as inline image in the email
            logger.debug("Adding logo as inline image")
            logo_path = os.path.join(os.path.dirname(__file__), '../images/logo.png')
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
        # Loads an email template using Jinja2, fills it with the provided context, and returns the rendered email body
        try:
            logger.debug(f"Loading email template '{template_name}'")
            # Prepare additional context
            context.update({
                'do_not_respond': self.translations["email"]["do_not_respond"],
                'footer': f"{self.translations["email"]["footer"] - {datetime.now().strftime('%d.%m.%Y')}}",
            })

            # Load and render the template
            template = self.jinja_env.get_template(template_name)
            full_body = template.render(context)
            logger.debug("Email body rendered using Jinja2")
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