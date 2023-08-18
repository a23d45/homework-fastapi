from datetime import timedelta

from celery import Celery

from config import RABBITMQ_DEFAULT_PASS as PASSWORD
from config import RABBITMQ_DEFAULT_USER as USER
from config import RABBITMQ_HOST as HOST
from menu_app.tasks.update_db import update_db_from_excel

broker_url = f'amqp://{USER}:{PASSWORD}@{HOST}'

celery = Celery('tasks', broker_url=broker_url)


@celery.task
def update_db_every_15_seconds():
    update_db_from_excel()


celery.conf.beat_schedule = {
    'update_db_every_15_seconds': {
        'task': 'menu_app.tasks.tasks.update_db_every_15_seconds',
        'schedule': timedelta(seconds=15),
    },
}
celery.conf.timezone = 'UTC'
