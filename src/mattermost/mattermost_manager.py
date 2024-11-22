from src.mattermost.mattermost_controller import MattermostController
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.logmgr import logger
from src.database.connection import get_db
from src.database.models.user import User
from src.database.models.transaction import Transaction
from src.database.models.item import Item
from datetime import datetime, timedelta
from src.localization.translator import get_translations

mattermost_controller = None
scheduler = None

def initialize_mattermost_controller(base_url: str, bot_token: str):
    """Initialize the MattermostController and the scheduler."""
    global mattermost_controller
    mattermost_controller = MattermostController(base_url=base_url, bot_token=bot_token)
    initialize_scheduler()

def get_mattermost_controller():
    global mattermost_controller
    if mattermost_controller is None:
        logger.error("Mattermost-Controller is not initialized")
    return mattermost_controller

def initialize_scheduler():
    """Initialize the APScheduler to run monthly summaries."""
    global scheduler
    logger.debug("Initializing scheduler")
    scheduler = BackgroundScheduler()
    # Schedule the job to run on the first day of every month at 00:00
    scheduler.add_job(send_monthly_summaries, CronTrigger(day=1, hour=0, minute=0))
    scheduler.start()
    logger.info("Scheduler started")

def send_monthly_summaries():
    """Send monthly summaries to all users."""
    logger.debug("Starting to send monthly summaries")
    # Get the current session
    session = get_db()
    # Get all users from the database using read_all class method
    users = User.read_all(session)
    for user in users:
        # Generate the summary for the user
        summary = get_monthly_summary(user, session)
        # Send the message if the user has a Mattermost username
        if user.mattermost_username:
            mattermost_controller.send_direct_message(
                username=user.mattermost_username,
                message=summary
            )
            logger.info(f"Monthly summary sent to user {user.name} ({user.mattermost_username})")
        else:
            logger.warning(f"User {user.name} does not have a Mattermost username, skipping.")
    logger.info("Monthly summaries have been sent to all users")

def get_monthly_summary(user, session):
    """Generate a monthly summary for a given user."""
    translations = get_translations()

    # Calculate the date range for the last month
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)

    # Get all transactions of the user within the date range
    transactions = Transaction.read_all_for_user(session, user.id)

    # Filter transactions within the date range
    transactions_in_last_month = [
        t for t in transactions if first_day_of_last_month <= t.date <= last_day_of_last_month
    ]

    # Calculate the total amount and aggregate product purchases
    total_amount = 0.0
    product_purchases = {}

    for t in transactions_in_last_month:
        total_amount += t.cost

        item = Item.get_by_id(session, item_id=t.item_id) if t.item_id else None
        product_name = item.name if item else "Unknown Product"

        if product_name in product_purchases:
            product_purchases[product_name]["quantity"] += 1
            product_purchases[product_name]["total_cost"] += t.cost
        else:
            product_purchases[product_name] = {
                "quantity": 1,
                "total_cost": t.cost
            }

    # Prepare the summary
    summary = translations["monthly_summary"]["title"].format(name=user.name) + "\n"
    summary += translations["monthly_summary"]["period"].format(
        start_date=first_day_of_last_month.strftime('%d.%m.%Y'),
        end_date=last_day_of_last_month.strftime('%d.%m.%Y')
    ) + "\n"
    summary += translations["monthly_summary"]["total_spent"].format(total_amount=total_amount) + "\n"
    summary += translations["monthly_summary"]["transaction_count"].format(transaction_count=len(transactions_in_last_month)) + "\n\n"
    summary += translations["monthly_summary"]["product_table_header"] + "\n"

    for product_name, details in product_purchases.items():
        summary += translations["monthly_summary"]["product_table_row"].format(
            product_name=product_name,
            quantity=details['quantity'],
            total_cost=details['total_cost']
        ) + "\n"

    summary += "\n" + translations["monthly_summary"]["footer"]

    return summary

def shutdown_scheduler():
    """Shutdown the scheduler and Mattermost controller."""
    global scheduler, mattermost_controller
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler shut down")
    if mattermost_controller:
        mattermost_controller.stop()
        logger.info("MattermostController thread stopped")