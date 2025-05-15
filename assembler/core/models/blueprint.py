"""Model for managing product blueprints and associated metadata.

This module defines the Blueprint model, which includes information about
the weight, scale, version, responsible users, and attached CAD/PDF files
related to a technical design.
"""

from typing import ClassVar

from django.core.validators import FileExtensionValidator, MinValueValidator

from core.models.base import NormalizeMixin, ReprMixin, _, models, user_fk


class Blueprint(ReprMixin, NormalizeMixin, models.Model):
    """Model representing a technical blueprint of a product.

    Stores information such as drawing scale, version, naming convention,
    associated users (developer, approver, etc.), and related files (PDF and STEP).
    """

    weight = models.DecimalField(
        _("Вес (кг)"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_("Вес изделия в килограммах (может быть пустым)"),
    )

    scale = models.CharField(
        _("Масштаб"),
        max_length=50,
        blank=True,
        help_text=_("Масштаб чертежа, например '1:10'"),
    )

    version = models.CharField(
        _("Версия"),
        max_length=50,
        blank=True,
        help_text=_("Версия чертежа, например 'v1.0'"),
    )

    naming_scheme = models.CharField(
        _("Схема наименования"),
        max_length=100,
        help_text=_("Схема наименования для идентификации чертежа"),
    )

    developer = user_fk(
        related_name="developed_blueprints",
        verbose_name=_("Разработчик"),
        help_text=_("Пользователь, разработавший чертёж"),
    )

    validator = user_fk(
        related_name="validated_blueprints",
        verbose_name=_("Проверяющий"),
        help_text=_("Пользователь, проверивший чертёж"),
    )

    lead_designer = user_fk(
        related_name="lead_designed_blueprints",
        verbose_name=_("Ведущий конструктор"),
        help_text=_("Ответственный ведущий конструктор проекта"),
    )

    chief_designer = user_fk(
        related_name="chief_designed_blueprints",
        verbose_name=_("Главный конструктор"),
        help_text=_("Главный конструктор проекта"),
    )

    approver = user_fk(
        related_name="approved_blueprints",
        verbose_name=_("Утвердивший"),
        help_text=_("Пользователь, утвердивший чертёж"),
    )

    scheme_file = models.FileField(
        upload_to="blueprints/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name=_("Файл чертежа (PDF)"),
        help_text=_("Загруженный файл чертежа в формате PDF"),
    )

    step_file = models.FileField(
        upload_to="steps/",
        validators=[FileExtensionValidator(allowed_extensions=["step"])],
        verbose_name=_("Файл чертежа (STEP)"),
        help_text=_("3D-модель в формате STEP для CAD-систем"),
    )

    def __str__(self) -> str:
        """Str representation of the blueprint."""
        return f"Blueprint #{self.pk} — Версия {self.version or 'N/A'}"

    class Meta:
        """Model metadata for Blueprint."""

        db_table: ClassVar[str] = "blueprints"
        verbose_name: ClassVar[str] = _("Чертёж")
        verbose_name_plural: ClassVar[str] = _("Чертежи")
        ordering: ClassVar[list[str]] = ["-id"]
