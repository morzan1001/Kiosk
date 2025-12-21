"""
Email Manager Module.
Provides initialization and access functions for the EmailController.
"""

from typing import Any, Dict, Optional

from src.app_context import get_app_context
from src.database.connection import get_new_session
from src.database.models.user import User
from src.localization.translator import get_system_language
from src.logmgr import logger
from src.messaging.utils import get_monthly_summary_data, initialize_scheduler

from .email_controller import EmailController


def initialize_email_controller(server: str, port: int, login: str, password: str) -> None:
    """
    Initialize the EmailController and the scheduler.

    Args:
        server: SMTP server address.
        port: SMTP server port.
        login: SMTP login username.
        password: SMTP login password.
    """
    ctx = get_app_context()
    ctx.email_controller = EmailController(
        smtp_server=server, smtp_port=port, login=login, password=password
    )
    ctx._scheduler_email = initialize_scheduler(send_monthly_summaries)


def get_email_controller() -> Optional[EmailController]:
    """
    Get the initialized EmailController instance.

    Returns:
        The EmailController instance or None if not initialized.
    """
    ctx = get_app_context()
    if ctx.email_controller is None:
        logger.error("Email-Controller is not initialized")
    return ctx.email_controller


def send_monthly_summaries() -> None:
    """Send monthly summaries to all users."""
    logger.debug("Starting to send monthly summaries")
    ctx = get_app_context()
    session = get_new_session()
    try:
        users = User.read_all(session)
        for user in users:
            summary = get_monthly_summary(user, session)
            if user.email and ctx.email_controller:
                ctx.email_controller.send_monthly_summary(
                    recipient=user.email,
                    summary=summary,
                    language=get_system_language(),
                )
                logger.info("Monthly summary sent to user %s (%s)", user.name, user.email)
            else:
                logger.warning("User %s does not have an email address, skipping.", user.name)
        logger.info("Monthly summaries have been sent to all users")
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Error sending monthly summaries")
    finally:
        session.close()


def get_monthly_summary(user: User, session: Any) -> Dict[str, Any]:
    """
    Generate a monthly summary for a given user.

    Args:
        user: The user to generate the summary for.
        session: Database session.

    Returns:
        Dictionary containing summary data.
    """
    (
        total_amount,
        product_purchases,
        first_day_of_last_month,
        last_day_of_last_month,
    ) = get_monthly_summary_data(user, session)

    summary: Dict[str, Any] = {
        "total_transactions": sum(p["quantity"] for p in product_purchases.values()),
        "total_amount": total_amount,
        "period": (
            f"{first_day_of_last_month.strftime('%d.%m.%Y')} - "
            f"{last_day_of_last_month.strftime('%d.%m.%Y')}"
        ),
        "product_purchases": product_purchases,
    }
    return summary


def shutdown_scheduler() -> None:
    """Shutdown the scheduler and email controller."""
    ctx = get_app_context()
    if ctx._scheduler_email:
        ctx._scheduler_email.shutdown()
        ctx._scheduler_email = None
        logger.info("Scheduler shut down")
    if ctx.email_controller:
        ctx.email_controller.stop()
        ctx.email_controller = None
        logger.info("EmailController thread stopped")
