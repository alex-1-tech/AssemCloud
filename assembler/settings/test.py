"""Django test settings for assembler project."""

from .base import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "test_assembler_db",
        "USER": "alex",
        "PASSWORD": config("PASSWORD"),  # noqa: F405
        "HOST": "localhost",
        "PORT": "3306",
    },
}
