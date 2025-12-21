"""Email messaging controller implementation."""

import os
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader, TemplateError

from src.localization.translator import get_translations
from src.logmgr import logger
from src.messaging.base_messaging_controller import BaseMessagingController
from src.utils.paths import get_image_path


class EmailController(BaseMessagingController):
    """Manages email notifications by sending dynamic, template-based emails via SMTP."""

    def __init__(self, smtp_server, smtp_port, login, password):
        logger.debug("Initializing EmailController with SMTP server details")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.login = login
        self.password = password
        self.translations = get_translations()
        logger.debug("Translations loaded")

        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        logger.debug("Jinja2 environment set up")

        # Initialize the base class (threading and queue)
        super().__init__()

    def get_channel_type(self):
        """Returns the message channel type."""
        return "email"

    def _send_message_internal(self, recipient, message, subject=None, **kwargs):
        """Internal implementation for sending an email."""
        is_html = kwargs.get("is_html", False)
        self._send_email(recipient, subject or "Nachricht", message, is_html)

    def _notify_low_balance_internal(self, recipient, balance, language="en"):
        """Internal implementation for low-balance notifications."""
        translated_subject = self.translations["email"]["low_balance_subject"]
        template_file = f"low_balance_{language}.html"
        body = self.load_template(template_file, {"balance": f"{balance:.2f}"})
        self._send_email(recipient, translated_subject, body, is_html=True)

    def _notify_low_stock_internal(
        self, recipient, product_name, available_quantity, language="en"
    ):
        """Internal implementation for low stock notifications."""
        translated_subject = self.translations["email"]["low_stock_subject"]
        template_file = f"product_low_stock_{language}.html"
        body = self.load_template(
            template_file,
            {"product_name": product_name, "available_quantity": available_quantity},
        )
        self._send_email(recipient, translated_subject, body, is_html=True)

    def _send_monthly_summary_internal(self, recipient, summary, language="en"):
        """Internal implementation for monthly summaries."""
        translated_subject = self.translations["email"]["monthly_summary_subject"]
        template_file = f"monthly_summary_{language}.html"
        body = self.load_template(template_file, {"summary": summary})
        self._send_email(recipient, translated_subject, body, is_html=True)

    def _send_email(self, recipient_email, subject, body, is_html):
        """Internal method for actually sending the email."""
        try:
            logger.debug("Sending email to %s with subject '%s'", recipient_email, subject)
            msg = MIMEMultipart("related")
            msg["From"] = self.login
            msg["To"] = recipient_email
            msg["Subject"] = subject

            body_part = MIMEText(body, "html" if is_html else "plain", "utf-8")
            msg.attach(body_part)
            logger.debug("Email body attached")

            # Add logo as inline image
            try:
                logger.debug("Adding logo as inline image")
                logo_path = get_image_path("logo.png")
                with open(logo_path, "rb") as img_file:
                    img_data = img_file.read()
                image = MIMEImage(img_data, name="logo.png")
                image.add_header("Content-ID", "<logo>")
                msg.attach(image)
            except OSError as e:
                logger.warning("Failed to attach logo image: %s", e)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.login, self.password)
                server.send_message(msg)

            logger.info("Email sent to %s", recipient_email)
        except OSError as e:
            logger.error("Failed to send email: %s", e)

    def load_template(self, template_name, context):
        """Loads and renders an email template."""
        try:
            logger.debug("Loading email template '%s'", template_name)
            footer_text = self.translations["email"]["footer"]
            current_date = datetime.now().strftime("%d.%m.%Y")

            context.update(
                {
                    "do_not_respond": self.translations["email"]["do_not_respond"],
                    "footer": f"{footer_text} - {current_date}",
                }
            )

            template = self.jinja_env.get_template(template_name)
            full_body = template.render(context)
            logger.debug("Email body rendered using Jinja2")
            return full_body
        except TemplateError as e:
            logger.error("Failed to load template %s: %s", template_name, e)
            return ""
