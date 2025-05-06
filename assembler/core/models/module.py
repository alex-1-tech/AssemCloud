from core.models.base import _, models, TimeStampedModelWithUser, NormalizeMixin, ReprMixin
from django.core.validators import MinLengthValidator


class Module(ReprMixin, NormalizeMixin, TimeStampedModelWithUser):
    """
    Модель для хранения информации о модулях.
    """
    machine = models.ForeignKey(
        'Machine',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='modules',
        verbose_name=_("Машина")
    )

    blueprint = models.OneToOneField(
        'Blueprint',
        on_delete=models.CASCADE,
        verbose_name=_("Чертёж")
    )

    part_number = models.CharField(
        "Артикул",
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(3)]
    )

    serial = models.CharField(
        _("Серийный номер"),
        max_length=100,
        null=True,
        blank=True
    )

    name = models.CharField(
        _("Название модуля"),
        max_length=255,
        null=True,
        blank=True
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submodules',
        verbose_name=_("Родительский модуль")
    )

    version = models.CharField(
        _("Версия"),
        max_length=50,
        null=True,
        blank=True
    )

    description = models.TextField(
        _("Описание"),
        null=True,
        blank=True
    )

    class ModuleStatus(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('В разработке')
        COMPLETED = 'completed', _('Завершен')
        CANCELLED = 'cancelled', _('Отменен')

    module_status = models.CharField(
        _("Статус"),
        max_length=20,
        choices=ModuleStatus.choices,
        default=ModuleStatus.IN_PROGRESS
    )

    def __str__(self):
        return f"{self.name or 'Без названия'} (S/N: {self.serial or 'нет'})"

    def clean(self):
        super().clean()
        if self.serial:
            self.serial = self.serial.lower()

    class Meta:
        db_table = 'modules'
        ordering = ['-updated_on']
        verbose_name = _("Модуль")
        verbose_name_plural = _("Модули")
        indexes = [
            models.Index(fields=['serial']),
            models.Index(fields=['part_number']),
            models.Index(fields=['name']),
            models.Index(fields=['machine', 'serial']),
        ]
