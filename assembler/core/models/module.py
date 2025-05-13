from django.core.validators import MinLengthValidator

from core.models.base import (
    NormalizeMixin,
    ReprMixin,
    TimeStampedModelWithUser,
    _,
    models,
)


class Module(ReprMixin, NormalizeMixin, TimeStampedModelWithUser):
    """
    Модель для хранения информации о модулях.

    Эта модель используется для описания различных модулей, которые могут быть частью
    машины. Включает информацию о чертеже, артикуле, серийном номере, статусе и других
    характеристиках модуля. Также поддерживает возможность установки родительского модуля,
    если модуль является подмодулем.
    """

    # Связь с моделью 'Machine'. Машина, к которой относится модуль.
    machine = models.ForeignKey(
        "Machine",
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name=_("Машина"),
    )

    # Связь с моделью 'Blueprint'. Каждый модуль связан с конкретным чертежом.
    blueprint = models.OneToOneField(
        "Blueprint",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Чертёж"),
    )

    # Артикул модуля. Уникальное поле с минимальной длиной 3 символа.
    part_number = models.CharField(
        "Артикул",
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(3)],
    )

    # Серийный номер модуля (обязательное поле).
    serial = models.CharField(
        _("Серийный номер"),
        max_length=100,
    )

    # Название модуля (обязательное поле).
    name = models.CharField(
        _("Название модуля"),
        max_length=255,
    )

    # Родительский модуль (если данный модуль является подмодулем).
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submodules",
        verbose_name=_("Родительский модуль"),
    )

    # Версия модуля (обязательное поле).
    version = models.CharField(
        _("Версия"),
        max_length=50,
    )

    # Описание модуля (необязательное поле).
    description = models.TextField(_("Описание"), null=True, blank=True)

    # Статус модуля. Возможные значения: в разработке, завершен, отменен.
    class ModuleStatus(models.TextChoices):
        IN_PROGRESS = "in_progress", _("В разработке")
        COMPLETED = "completed", _("Завершен")
        CANCELLED = "cancelled", _("Отменен")

    module_status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=ModuleStatus.choices,
        default=ModuleStatus.IN_PROGRESS,
    )

    def __str__(self):
        return f"{self.name or 'Без названия'} (S/N: {self.serial or 'нет'})"

    class Meta:
        db_table = "modules"
        ordering = ["-updated_on"]
        verbose_name = _("Модуль")
        verbose_name_plural = _("Модули")
        indexes = [
            models.Index(fields=["serial"]),
            models.Index(fields=["part_number"]),
            models.Index(fields=["name"]),
            models.Index(fields=["machine", "serial"]),
        ]
