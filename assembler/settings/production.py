"""Django production settings for assembler project."""
import os

from .base import *  # noqa: F403

DEBUG = False
# ALLOWED_HOSTS = ["votum.asuscomm.com", "37.203.240.41", "localhost", "127.0.0.1"]  # noqa: E501, ERA001
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405, PTH118

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
