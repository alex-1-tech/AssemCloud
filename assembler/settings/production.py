"""Django production settings for assembler project."""
import os

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = [
    "cloud.pulsarndt.ae",
    "217.165.161.126",
    "localhost",
    "127.0.0.1",
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405, PTH118

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = ["https://cloud.pulsarndt.ae"]