"""Django production settings for assembler project."""
from pathlib import Path

from .base import BASE_DIR

DEBUG = True
# ALLOWED_HOSTS = ["votum.asuscomm.com", "37.203.240.41", "localhost", "127.0.0.1"]  # noqa: E501, ERA001
STATIC_ROOT = Path(BASE_DIR) / "staticfiles"

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
