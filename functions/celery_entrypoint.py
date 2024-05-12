from dotenv import load_dotenv
load_dotenv("./.api.env")

from infrastructure.celery import celery_app
