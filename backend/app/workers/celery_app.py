from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "price_tracker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.beat_schedule = {
    "scrape-all-products": {
        "task": "app.workers.tasks.scrape_all_products",
        "schedule": crontab(minute="*/30"),
    },
}

celery_app.conf.timezone = "Europe/Warsaw"
