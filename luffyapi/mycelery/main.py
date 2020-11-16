from celery import Celery

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luffyapi.settings.dev')
import django
django.setup()

app = Celery()
app.config_from_object('mycelery.config')
app.autodiscover_tasks(['mycelery.sms', 'mycelery.order'])

# 运行celery
# celery -A mycelery.main worker --loglevel=info




