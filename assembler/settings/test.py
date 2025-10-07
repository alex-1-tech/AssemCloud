"""Django test settings for assembler project."""

from .base import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "test_assembler_db",
        "USER":  config("USER"),  # noqa: F405
        "PASSWORD": config("PASSWORD"),  # noqa: F405
        "HOST":  config("HOST"),  # noqa: F405
        "PORT": "3306",
    },
}
