from __future__ import unicode_literals
import os

PROJECT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), 'django_calculated_field'))
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(PROJECT_ROOT, 'templates')]}]

SECRET_KEY = 'NOTREALLY'
PAYMENT_HOST = 'example.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "/tmp/test_db",
    }
}

INSTALLED_APPS = ['django_calculated_field', 'south']

