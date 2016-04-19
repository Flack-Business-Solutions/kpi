# http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
from __future__ import absolute_import
import os
import celery

from django.conf import settings
from raven.contrib.celery import register_signal, register_logger_signal
from raven.contrib.django.raven_compat.models import client as raven_client

# Attempt to determine the project name from the directory containing this file
PROJECT_NAME = os.path.basename(os.path.dirname(__file__))

# Set the default Django settings module for the 'celery' command-line program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{}.settings'.format(
    PROJECT_NAME))

# Log to Sentry from Celery jobs per
# https://docs.getsentry.com/hosted/clients/python/integrations/celery/
class Celery(celery.Celery):
    def on_configure(self):
        # register a custom filter to filter out duplicate logs
        register_logger_signal(raven_client)
        # hook into the Celery error handler
        register_signal(raven_client)

app = Celery(PROJECT_NAME)
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')

# The `app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)` technique
# described in
# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
# fails when INSTALLED_APPS includes a "dotted path to the appropriate
# AppConfig subclass" as recommended by
# https://docs.djangoproject.com/en/1.8/ref/applications/#configuring-applications.
# Ask Solem recommends the following workaround; see
# https://github.com/celery/celery/issues/2248#issuecomment-97404667
from django.apps import apps
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
