"""Django development settings for assembler project."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "assembler_db",
        "USER": "alex",
        "PASSWORD": config("PASSWORD"),  # noqa: F405
        "HOST": "localhost",
        "PORT": "3306",
    },
}
