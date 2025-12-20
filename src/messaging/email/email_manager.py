from src.database.connection import get_new_session
from src.database.models.user import User
from src.localization.translator import get_system_language
from src.logmgr import logger
from src.messaging.utils import get_monthly_summary_data, initialize_scheduler

from .email_controller import EmailController

EMAIL_CONTROLLER = None
SCHEDULER = None


def initialize_email_controller(server: str, port: int, login: str, password: str):
    """Initialize the EmailController and the scheduler."""
    global EMAIL_CONTROLLER, SCHEDULER
    EMAIL_CONTROLLER = EmailController(
        smtp_server=server, smtp_port=port, login=login, password=password
    )
    SCHEDULER = initialize_scheduler(send_monthly_summaries)


def get_email_controller() -> EmailController:
    """Get the initialized EmailController instance."""
    if EMAIL_CONTROLLER is None:
        logger.error("Email-Controller is not initialized")
    return EMAIL_CONTROLLER


def send_monthly_summaries():
    """Send monthly summaries to all users."""
    logger.debug("Starting to send monthly summaries")
    session = get_new_session()
    try:
        users = User.read_all(session)
        for user in users:
            summary = get_monthly_summary(user, session)
            if user.email:
                EMAIL_CONTROLLER.send_monthly_summary(
                    recipient=user.email,
                    summary=summary,
                    language=get_system_language(),
                )
                logger.info(f"Monthly summary sent to user {user.name} ({user.email})")
            else:
                logger.warning(
                    f"User {user.name} does not have an email address, skipping."
                )
        logger.info("Monthly summaries have been sent to all users")
    except Exception as e:
        logger.error(f"Error sending monthly summaries: {e}")
    finally:
        session.close()


def get_monthly_summary(user, session):
    """Generate a monthly summary for a given user."""
    (
        total_amount,
        product_purchases,
        first_day_of_last_month,
        last_day_of_last_month,
    ) = get_monthly_summary_data(user, session)

    summary = {
        "total_transactions": sum(p["quantity"] for p in product_purchases.values()),
        "total_amount": total_amount,
        "period": f"{first_day_of_last_month.strftime('%d.%m.%Y')} - {last_day_of_last_month.strftime('%d.%m.%Y')}",
        "product_purchases": product_purchases,
    }
    return summary


def shutdown_scheduler():
    """Shutdown the scheduler and email controller."""
    if SCHEDULER:
        SCHEDULER.shutdown()
        logger.info("Scheduler shut down")
    if EMAIL_CONTROLLER:
        EMAIL_CONTROLLER.stop()
        logger.info("EmailController thread stopped")
