"""App configuration for the core application."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration class for the core app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self) -> None:
        """Import signal handlers to ensure they are registered."""
        import core.signals  # noqa: F401
