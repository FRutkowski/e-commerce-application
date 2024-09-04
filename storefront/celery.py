import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storefront.settings")

celery = Celery("storefront")
celery.config_from_object("django.conf:settings", namespace="CELERY")
# aby samo znajdowało taski
celery.autodiscover_tasks()
