import os
# from celery.schedules import crontab

from .settings import *

DEBUG = os.environ.get("DEBUG", default=1)


DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE"),
        "NAME": os.environ.get("SQL_DATABASE"),
        "USER": os.environ.get("SQL_USER"),
        "PASSWORD": os.environ.get("SQL_PASSWORD"),
        "HOST": os.environ.get("SQL_HOST"),
        "PORT": os.environ.get("SQL_PORT"),
    },
}


# CELERY_BEAT_SCHEDULE = {
#     "vegitables-daily-price": {
#         "task": "vegitable-daily-price",
#         "schedule": crontab(minute="*"),
#     },
# }
