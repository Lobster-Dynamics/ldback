import os
from celery import Celery

# celery config
class Config:
    ...

celery_app = Celery("tasks", broker=os.environ["AMQP_URL"])
