"""
Utility functions for messaging modules.
"""

from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.database.models.item import Item
from src.database.models.transaction import Transaction
from src.logmgr import logger


def initialize_scheduler(job_function):
    """Initialize the APScheduler to run monthly summaries."""
    logger.debug("Initializing scheduler")
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_function, CronTrigger(day=1, hour=0, minute=0))
    scheduler.start()
    logger.info("Scheduler started")
    return scheduler


def get_monthly_summary_data(user, session):
    """
    Generate monthly summary data for a given user.
    Returns a tuple (total_amount, product_purchases, start_date, end_date).
    """
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)

    transactions = Transaction.read_all_for_user(session, user.id)

    transactions_in_last_month = [
        t for t in transactions if first_day_of_last_month <= t.date <= last_day_of_last_month
    ]

    total_amount = 0.0
    product_purchases = {}

    for t in transactions_in_last_month:
        cost = float(t.cost)
        total_amount += cost

        item = Item.get_by_id(session, item_id=t.item_id) if t.item_id else None
        product_name = item.name if item else "Unknown Product"

        if product_name in product_purchases:
            product_purchases[product_name]["quantity"] += 1
            product_purchases[product_name]["total_cost"] += cost
        else:
            product_purchases[product_name] = {
                "quantity": 1,
                "total_cost": cost,
            }

    return (
        total_amount,
        product_purchases,
        first_day_of_last_month,
        last_day_of_last_month,
    )
