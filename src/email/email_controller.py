import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from src.logmgr import logger
from src.localization.translator import get_translations  # Import translations
import os

class EmailController:
    def __init__(self, smtp_server, smtp_port, login, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.login = login
        self.password = password
        self.translations = get_translations()  # Fetch translations

    def send_email(self, recipient_email, subject, body, is_html=False):
        try:
            logger.debug(f"Preparing to send email to {recipient_email}")
            msg = MIMEMultipart()
            msg['From'] = self.login
            msg['To'] = recipient_email
            msg['Subject'] = subject

            body_part = MIMEText(body, 'html' if is_html else 'plain')
            msg.attach(body_part)

            # Add logo as inline image
            logo_path = os.path.join(os.path.dirname(__file__), '../../assets/logo.png')
            with open(logo_path, 'rb') as img_file:
                img_data = img_file.read()
            image = MIMEImage(img_data, name='logo.png')
            image.add_header('Content-ID', '<logo>')
            msg.attach(image)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.login, self.password)
                server.send_message(msg)

            logger.info(f"Email sent to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def load_template(self, template_name, context):
        try:
            template_path = os.path.join(os.path.dirname(__file__), 'templates', template_name)
            with open(template_path, 'r', encoding='utf-8') as file:
                content_template = file.read()

            base_template_path = os.path.join(os.path.dirname(__file__), 'templates', 'base.html')
            with open(base_template_path, 'r', encoding='utf-8') as base_file:
                base_template = base_file.read()
            
            # Define the footer text and append the current date
            footer_text = self.translations["email"]["footer"]
            current_date = datetime.now().strftime("%d.%m.%Y")
            footer_with_date = f"{footer_text} - {current_date}"

            do_not_respond = self.translations["email"]["do_not_respond"]

            content = content_template.format(**context)
            full_body = base_template.replace("{{ content }}", content).replace("{{ do_not_responde }}", do_not_respond).replace("{{ footer }}", footer_with_date)
            return full_body
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return ""

    def notify_low_balance(self, recipient_email, balance, language='de'):
        translated_subject = self.translations["email"]["low_balance_subject"]
        template_file = f"low_balance_{language}.html"
        body = self.load_template(template_file, {"balance": balance})
        self.send_email(recipient_email, translated_subject, body, is_html=True)

    def send_monthly_summary(self, recipient_email, summary, language='de'):
        translated_subject = self.translations["email"]["monthly_summary_subject"]
        template_file = f"monthly_summary_{language}.html"
        body = self.load_template(template_file, {"summary": summary})
        self.send_email(recipient_email, translated_subject, body, is_html=True)