from .base import *

DEBUG = False
ALLOWED_HOSTS = ['-']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'assembler_db',
        'USER': 'alex',
        'PASSWORD': 'ysn;r35',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
