from src.database.connection import get_db
from src.database.models.user import User
from src.localization.translator import get_translations
from src.logmgr import logger
from src.messaging.utils import get_monthly_summary_data, initialize_scheduler

from .mattermost_controller import MattermostController

MATTERMOST_CONTROLLER = None
SCHEDULER = None


def initialize_mattermost_controller(base_url: str, bot_token: str):
    """Initialize the MattermostController and the scheduler."""
    global MATTERMOST_CONTROLLER, SCHEDULER
    MATTERMOST_CONTROLLER = MattermostController(base_url=base_url, bot_token=bot_token)
    SCHEDULER = initialize_scheduler(send_monthly_summaries)


def get_mattermost_controller():
    """Get the initialized MattermostController instance."""
    if MATTERMOST_CONTROLLER is None:
        logger.error("Mattermost-Controller is not initialized")
    return MATTERMOST_CONTROLLER


def send_monthly_summaries():
    """Send monthly summaries to all users."""
    logger.debug("Starting to send monthly summaries")
    session = get_db()
    users = User.read_all(session)
    for user in users:
        summary = get_monthly_summary(user, session)
        if user.mattermost_username:
            MATTERMOST_CONTROLLER.send_message(
                recipient=user.mattermost_username, message=summary
            )
            logger.info(
                f"Monthly summary sent to user {user.name} ({user.mattermost_username})"
            )
        else:
            logger.warning(
                f"User {user.name} does not have a Mattermost username, skipping."
            )
    logger.info("Monthly summaries have been sent to all users")


def get_monthly_summary(user, session):
    """Generate a monthly summary for a given user."""
    # pylint: disable=invalid-sequence-index
    translations: dict = get_translations()

    data = get_monthly_summary_data(user, session)

    summary = translations["monthly_summary"]["title"].format(name=user.name) + "\n"
    summary += (
        translations["monthly_summary"]["period"].format(
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
        + "\n"
    )
    summary += (
        translations["monthly_summary"]["total_spent"].format(
            total_amount=data["total_amount"]
        )
        + "\n"
    )
    summary += (
        translations["monthly_summary"]["transaction_count"].format(
            transaction_count=data["transaction_count"]
        )
        + "\n\n"
    )
    summary += translations["monthly_summary"]["product_table_header"] + "\n"

    for product_name, details in data["product_purchases"].items():
        summary += (
            translations["monthly_summary"]["product_table_row"].format(
                product_name=product_name,
                quantity=details["quantity"],
                total_cost=details["total_cost"],
            )
            + "\n"
        )

    summary += "\n" + translations["monthly_summary"]["footer"]

    return summary


def shutdown_scheduler():
    """Shutdown the scheduler and Mattermost controller."""
    if SCHEDULER:
        SCHEDULER.shutdown()
        logger.info("Scheduler shut down")
    if MATTERMOST_CONTROLLER:
        MATTERMOST_CONTROLLER.stop()
        logger.info("MattermostController thread stopped")
