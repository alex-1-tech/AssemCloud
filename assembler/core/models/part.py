from core.models.base import (
    NormalizeMixin,
    ReprMixin,
    TimeStampedModelWithUser,
    _,
    models,
)


class Part(ReprMixin, NormalizeMixin, TimeStampedModelWithUser):
    """
    Модель для хранения информации о детали и её производстве.

    Эта модель описывает отдельную деталь, которая используется в различных модулях
    и включает в себя всю необходимую информацию о производственном процессе, 
    включая производителя, дату производства, материал и описание.

    Используется в связке с моделью ModulePart для определения количества 
    и размещения деталей в модулях.
    """

    # Название детали (обязательное поле)
    name = models.CharField(_("Название"), max_length=255)

    # Связь с моделью 'Manufacturer', указывающая, кто изготовил деталь
    manufacturer = models.ForeignKey(
        "Manufacturer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parts_manufactured",
        verbose_name=_("Производитель"),
    )

    # Описание детали (необязательное текстовое поле)
    part_description = models.TextField(_("Описание детали"), blank=True, null=True)

    # Материал, из которого изготовлена деталь (необязательное поле)
    material = models.CharField(_("Материал"), max_length=100, blank=True)

    # Дата производства детали (необязательное поле)
    manufacture_date = models.DateField(_("Дата производства"), blank=True, null=True)

    def __str__(self):
        # Возвращает строковое представление детали — её название
        return self.name

    class Meta:
        db_table = "parts"
        verbose_name = _("Деталь")
        verbose_name_plural = _("Детали")
        ordering = ["name"]
        indexes = [
            # Индекс для оптимизации фильтрации по дате
            models.Index(fields=["manufacture_date"]),
        ]



class ModulePart(ReprMixin, models.Model):
    """
    Модель для связывания деталей с модулями.

    Эта модель представляет связь между деталью и модулем, 
    описывая количество каждой детали,
    которая используется в конкретном модуле.
    """

    # Связь с моделью 'Module', указывающая, к какому модулю принадлежит деталь.
    module = models.ForeignKey(
        "Module",
        on_delete=models.CASCADE,
        related_name="module_parts",
        verbose_name=_("Модуль"),
    )

    # Связь с моделью 'Part', указывающая, какая деталь используется в модуле.
    part = models.ForeignKey(
        "Part",
        on_delete=models.RESTRICT,
        related_name="part_modules",
        verbose_name=_("Деталь"),
    )

    # Количество деталей, использующихся в модуле.
    quantity = models.PositiveIntegerField(
        _("Количество"), default=1, help_text=_("Количество деталей в модуле")
    )

    def __str__(self):
        return f"{self.module} × {self.part} ({self.quantity})"

    class Meta:
        db_table = "module_part"
        verbose_name = _("Связь Деталь-Модуль")
        verbose_name_plural = _("Связи Деталь-Модуль")
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0), name="quantity_positive"
            ),  # Проверка, что количество больше 0
            models.UniqueConstraint(
                fields=["module", "part"], name="unique_module_part"
            ),
        ]
