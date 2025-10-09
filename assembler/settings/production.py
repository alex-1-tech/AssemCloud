"""Django production settings for assembler project."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["votum.asuscomm.com", "37.203.240.41", "localhost", "127.0.0.1"]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405

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


SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
