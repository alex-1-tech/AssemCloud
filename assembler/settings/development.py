"""Django development settings for assembler project."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "assembler_db",
        "USER":  config("USER"),  # noqa: F405
        "PASSWORD": config("PASSWORD"),  # noqa: F405
        "HOST":  config("HOST"),  # noqa: F405
        "PORT": "3306",
    },
}
