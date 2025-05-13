from .base import * # noqa: F403 I001

DEBUG = False
ALLOWED_HOSTS = ["-"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "assembler_db",
        "USER": "alex",
        "PASSWORD": config("PASSWORD"), # noqa: F405
        "HOST": "localhost",
        "PORT": "3306",
    }
}


SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = config("") # noqa: F405
