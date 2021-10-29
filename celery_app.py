import os
from dotenv import load_dotenv

from celery import Celery

load_dotenv()

app = Celery("tasks", broker=os.environ.get("AMQP_URI"))
