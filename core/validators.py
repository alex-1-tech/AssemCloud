"""Custom validators for AssemCloud core models.

This module provides validation functions for serial number format and positive weight.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_weight_positive(value: float) -> None:
    """Validate of a positive weight."""
    if value < 0:
        raise ValidationError(
            _("Вес должен быть положительным числом"),
        )
