from localization.translator import get_translations
from src.mattermost.mattermost_controller import MattermostController
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.logmgr import logger
from src.database.connection import get_db
from src.database.models.user import User
from src.database.models.transaction import Transaction
from datetime import datetime, timedelta

mattermost_controller = None
scheduler = None
translations = get_translations()

def initialize_mattermost_controller(webhook_url: str):
    """Initialize the MattermostController and the scheduler."""
    global mattermost_controller
    mattermost_controller = MattermostController(webhook_url=webhook_url)
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
                message=f"Dein monatlicher Bericht: {summary}"
            )
            logger.info(f"Monthly summary sent to user {user.name} ({user.mattermost_username})")
        else:
            logger.warning(f"User {user.name} does not have a Mattermost username, skipping.")
    logger.info("Monthly summaries have been sent to all users")

def get_monthly_summary(user, session):
    """Generate a monthly summary for a given user."""
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
        product_name = t.item.name if t.item else "Unknown Product"

        if product_name in product_purchases:
            product_purchases[product_name]["quantity"] += 1
            product_purchases[product_name]["total_cost"] += t.cost
        else:
            product_purchases[product_name] = {
                "quantity": 1,
                "total_cost": t.cost
            }

    # Prepare the summary
    summary = f"**Monatlicher Bericht für {user.name}**\n"
    summary += f"Zeitraum: {first_day_of_last_month.strftime('%d.%m.%Y')} - {last_day_of_last_month.strftime('%d.%m.%Y')}\n"
    summary += f"Gesamtausgaben: {total_amount:.2f}€\n"
    summary += f"Anzahl der Transaktionen: {len(transactions_in_last_month)}\n\n"
    summary += "| Produkt | Menge | Gesamtkosten |\n"
    summary += "|---------|-------|--------------|\n"

    for product_name, details in product_purchases.items():
        summary += f"| {product_name} | {details['quantity']} | {details['total_cost']:.2f}€ |\n"

    summary += "\n:moneybag: Vielen Dank für deine Einkäufe! :moneybag:"

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