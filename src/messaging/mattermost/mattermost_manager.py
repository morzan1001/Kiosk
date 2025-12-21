"""
Mattermost Manager Module.
Provides initialization and access functions for the MattermostController.
"""

from typing import Any, Dict, Optional

from src.app_context import get_app_context
from src.database.connection import get_db
from src.database.models.user import User
from src.localization.translator import get_translations
from src.logmgr import logger
from src.messaging.utils import get_monthly_summary_data, initialize_scheduler

from .mattermost_controller import MattermostController


def initialize_mattermost_controller(base_url: str, bot_token: str) -> None:
    """
    Initialize the MattermostController and the scheduler.

    Args:
        base_url: Mattermost server base URL.
        bot_token: Bot authentication token.
    """
    ctx = get_app_context()
    ctx.mattermost_controller = MattermostController(base_url=base_url, bot_token=bot_token)
    ctx._scheduler_mattermost = initialize_scheduler(send_monthly_summaries)


def get_mattermost_controller() -> Optional[MattermostController]:
    """
    Get the initialized MattermostController instance.

    Returns:
        The MattermostController instance or None if not initialized.
    """
    ctx = get_app_context()
    if ctx.mattermost_controller is None:
        logger.error("Mattermost-Controller is not initialized")
    return ctx.mattermost_controller


def send_monthly_summaries() -> None:
    """Send monthly summaries to all users."""
    logger.debug("Starting to send monthly summaries")
    ctx = get_app_context()
    session = get_db()
    users = User.read_all(session)
    for user in users:
        summary = get_monthly_summary(user, session)
        if user.mattermost_username and ctx.mattermost_controller:
            ctx.mattermost_controller.send_message(
                recipient=user.mattermost_username, message=summary
            )
            logger.info(
                "Monthly summary sent to user %s (%s)",
                user.name,
                user.mattermost_username,
            )
        else:
            logger.warning(
                "User %s does not have a Mattermost username, skipping.",
                user.name,
            )
    logger.info("Monthly summaries have been sent to all users")


def get_monthly_summary(user: User, session: Any) -> str:
    """
    Generate a monthly summary for a given user.

    Args:
        user: The user to generate the summary for.
        session: Database session.

    Returns:
        Formatted summary string.
    """
    # pylint: disable=invalid-sequence-index
    translations: Dict[str, Any] = get_translations()

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
        translations["monthly_summary"]["total_spent"].format(total_amount=data["total_amount"])
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


def shutdown_scheduler() -> None:
    """Shutdown the scheduler and Mattermost controller."""
    ctx = get_app_context()
    if ctx._scheduler_mattermost:
        ctx._scheduler_mattermost.shutdown()
        ctx._scheduler_mattermost = None
        logger.info("Scheduler shut down")
    if ctx.mattermost_controller:
        ctx.mattermost_controller.stop()
        ctx.mattermost_controller = None
        logger.info("MattermostController thread stopped")
