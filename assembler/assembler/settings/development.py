from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

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
