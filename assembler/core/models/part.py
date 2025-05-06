from core.models.base import _, models, TimeStampedModelWithUser, NormalizeMixin, ReprMixin


class PartManufacture(ReprMixin, TimeStampedModelWithUser):
    """
    Модель для хранения информации о производстве деталей.

    Эта модель хранит информацию о процессе производства деталей, включая данные о 
    производителе, описание детали, используемый материал и дату производства.
    """
    
    # Связь с моделью 'Manufacturer', указывающая, какой производитель изготовил деталь.
    manufacturer = models.ForeignKey(
        'Manufacturer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parts_manufactured',
        verbose_name=_("Производитель")
    )
    
    # Описание детали (необязательное поле).
    part_description = models.TextField(
        _("Описание детали"), blank=True, null=True
    )
    
    # Материал, из которого изготовлена деталь (необязательное поле).
    material = models.CharField(
        _("Материал"), max_length=100, blank=True
    )
    
    # Дата производства детали (необязательное поле).
    manufacture_date = models.DateField(
        _("Дата производства"), blank=True, null=True
    )

    def __str__(self):
        return f"{self.manufacturer or _('Без производителя')} / {self.material or _('Материал не указан')}"

    class Meta:
        db_table = 'part_manufacture'
        verbose_name = _("Описание детали")
        verbose_name_plural = _("Описание деталей")
        ordering = ['-manufacture_date']
        indexes = [models.Index(fields=['manufacture_date'])]


class Part(ReprMixin, NormalizeMixin, TimeStampedModelWithUser):
    """
    Модель для хранения информации о деталях.

    Модель описывает отдельную деталь, которая может быть связана с производственным процессом
    и относится к конкретному модулю. Включает информацию о названии и производстве детали.
    """

    # Название детали.
    name = models.CharField(_("Название"), max_length=255)
    
    # Связь с моделью 'PartManufacture', указывающая, в рамках какого производства была изготовлена деталь.
    part_manufacture = models.ForeignKey(
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

    Эта модель представляет связь между деталью и модулем, описывая количество каждой детали,
    которая используется в конкретном модуле.
    """

    # Связь с моделью 'Module', указывающая, к какому модулю принадлежит деталь.
    module = models.ForeignKey(
        'Module',
        on_delete=models.CASCADE,
        related_name='module_parts',
        verbose_name=_("Модуль")
    )
    
    # Связь с моделью 'Part', указывающая, какая деталь используется в модуле.
    part = models.ForeignKey(
        'Part',
        on_delete=models.RESTRICT,
        related_name='part_modules',
        verbose_name=_("Деталь")
    )
    
    # Количество деталей, использующихся в модуле.
    quantity = models.PositiveIntegerField(
        _("Количество"),
        default=1,
        help_text=_("Количество деталей в модуле")
    )

    def __str__(self):
        return f"{self.module} × {self.part} ({self.quantity})"

    class Meta:
        db_table = 'module_part'
        verbose_name = _("Связь Деталь-Модуль")
        verbose_name_plural = _("Связи Деталь-Модуль")
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gt=0), name="quantity_positive"),  # Проверка, что количество больше 0
            models.UniqueConstraint(fields=['module', 'part'], name='unique_module_part')
        ]
