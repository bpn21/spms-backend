import os

from celery import Celery
from config.load_setting_module import DJANGO_SETTINGS_MODULE

# Set the default Django settings module for the 'celery' program.
os.environ["DJANGO_SETTINGS_MODULE"] = DJANGO_SETTINGS_MODULE

app = Celery("src.apps")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
