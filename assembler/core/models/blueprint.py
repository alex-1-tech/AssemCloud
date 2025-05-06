from core.models.base import _, models, user_fk, NormalizeMixin, ReprMixin
from django.core.validators import MinValueValidator, FileExtensionValidator
from core.models.user import User
from core.models.client import Manufacturer


class Blueprint(ReprMixin, NormalizeMixin, models.Model):
    """
    Модель для хранения чертежей.
    """
    weight = models.DecimalField(
        _("Вес (кг)"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    scale = models.CharField(_("Масштаб"), max_length=50, blank=True)
    version = models.CharField(_("Версия"), max_length=50, blank=True)
    naming_scheme = models.CharField(_("Схема наименования"), max_length=100, blank=True)

    developer = user_fk('developed_blueprints', _("Разработчик"))
    validator = user_fk('validated_blueprints', _("Проверяющий"))
    lead_designer = user_fk('lead_designed_blueprints', _("Ведущий конструктор"))
    chief_designer = user_fk('chief_designed_blueprints', _("Главный конструктор"))
    approver = user_fk('approved_blueprints', _("Утвердивший"))

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        verbose_name=_("Производитель")
    )

    scheme_file = models.FileField(
        upload_to='blueprints/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name=_('Файл чертежа (PDF)')
    )

    step_file = models.FileField(
        upload_to='steps/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['step'])],
        verbose_name=_('Файл чертежа (STEP)')
    )

    def __str__(self):
        return f"Blueprint #{self.pk} — Версия {self.version or 'N/A'}"

    class Meta:
        db_table = 'blueprints'
        verbose_name = _("Чертёж")
        verbose_name_plural = _("Чертежи")
        ordering = ['-id']
