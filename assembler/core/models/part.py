from core.models.base import _, models, TimeStampedModelWithUser, NormalizeMixin, ReprMixin


class PartManufacture(ReprMixin, TimeStampedModelWithUser):
    """
    Модель для хранения информации о производстве деталей.
    """
    manufacturer = models.ForeignKey(
        'Manufacturer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parts_manufactured',
        verbose_name=_("Производитель")
    )
    part_description = models.TextField(
        _("Описание детали"), blank=True, null=True
    )
    material = models.CharField(
        _("Материал"), max_length=100, blank=True
    )
    manufacture_date = models.DateField(
        _("Дата производства"), blank=True, null=True
    )

    def __str__(self):
        return f"{self.manufacturer or _('Без производителя')} / {self.material or _('Материал не указан')}"

    class Meta:
        db_table = 'part_manufacture'
        verbose_name = _("Производство детали")
        verbose_name_plural = _("Производства деталей")
        ordering = ['-manufacture_date']
        indexes = [models.Index(fields=['manufacture_date'])]



class Part(ReprMixin, NormalizeMixin, TimeStampedModelWithUser):
    """
    Модель для хранения информации о деталях.
    """
    name = models.CharField(_("Название"), max_length=255)
    manufacture = models.ForeignKey(
        PartManufacture,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='parts',
        verbose_name=_("Производство")
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'parts'
        verbose_name = _("Деталь")
        verbose_name_plural = _("Детали")
        ordering = ['name']


class ModulePart(ReprMixin, models.Model):
    """
    Модель для связывания деталей с модулями.
    """
    module = models.ForeignKey(
        'Module',
        on_delete=models.CASCADE,
        related_name='module_parts',
        verbose_name=_("Модуль")
    )
    part = models.ForeignKey(
        'Part',
        on_delete=models.RESTRICT,
        related_name='part_modules',
        verbose_name=_("Деталь")
    )
    quantity = models.PositiveIntegerField(
        _("Количество"),
        default=1,
        help_text=_("Количество деталей в модуле")
    )

    def __str__(self):
        return f"{self.module} × {self.part} ({self.quantity})"

    class Meta:
        db_table = 'module_part'
        verbose_name = _("Деталь модуля")
        verbose_name_plural = _("Детали модулей")
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gt=0), name="quantity_positive"),
            models.UniqueConstraint(fields=['module', 'part'], name='unique_module_part')
        ]
