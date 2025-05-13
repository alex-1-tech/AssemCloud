from django.core.validators import FileExtensionValidator, MinValueValidator

from core.models.base import NormalizeMixin, ReprMixin, _, models, user_fk
from core.models.client import Manufacturer


class Blueprint(ReprMixin, NormalizeMixin, models.Model):
    """
    Модель для хранения информации о чертежах изделия, включая связанные файлы,
    информацию об участниках разработки и дополнительную метаинформацию.
    """

    # Вес изделия, заданный в килограммах. Может быть пустым.
    weight = models.DecimalField(
        _("Вес (кг)"),
        max_digits=10,  # Максимум 10 знаков
        decimal_places=2,  # 2 знака после запятой
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],  # Вес не может быть отрицательным
    )

    # Масштаб чертежа, например "1:10"
    scale = models.CharField(_("Масштаб"), max_length=50, blank=True)

    # Версия чертежа, например "v1.0"
    version = models.CharField(_("Версия"), max_length=50, blank=True)

    # Схема наименования, используемая для идентификации чертежа
    naming_scheme = models.CharField(_("Схема наименования"), max_length=100)

    # Пользователь, разработавший чертёж
    developer = user_fk("developed_blueprints", _("Разработчик"))

    # Пользователь, проверивший чертёж
    validator = user_fk("validated_blueprints", _("Проверяющий"))

    # Ведущий конструктор, ответственный за проект
    lead_designer = user_fk("lead_designed_blueprints", _("Ведущий конструктор"))

    # Главный конструктор проекта
    chief_designer = user_fk("chief_designed_blueprints", _("Главный конструктор"))

    # Пользователь, утвердивший чертёж
    approver = user_fk("approved_blueprints", _("Утвердивший"))

    # Производитель, связанный с данным чертежом
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.RESTRICT,  # Запрет на удаление производителя, если есть связанные чертежи
        blank=True,
        null=True,
        verbose_name=_("Производитель"),
    )

    # PDF-файл с чертежом (визуальный вид)
    scheme_file = models.FileField(
        upload_to="blueprints/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        verbose_name=_("Файл чертежа (PDF)"),
    )

    # STEP-файл (3D-модель для CAD-систем)
    step_file = models.FileField(
        upload_to="steps/",
        validators=[FileExtensionValidator(allowed_extensions=["step"])],
        verbose_name=_("Файл чертежа (STEP)"),
    )

    def __str__(self):
        return f"Blueprint #{self.pk} — Версия {self.version or 'N/A'}"

    class Meta:
        db_table = "blueprints"
        verbose_name = _("Чертёж")
        verbose_name_plural = _("Чертежи")
        ordering = ["-id"]
