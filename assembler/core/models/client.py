from core.models.base import _, models, NormalizeMixin, PHONE_VALIDATOR, ReprMixin

class Client(ReprMixin, NormalizeMixin, models.Model):
    """
    Модель клиента.
    """

    # Название клиента (обязательно и уникально)
    name = models.CharField(_("Имя клиента"), max_length=150, unique=True)

    # Страна клиента (обязательное поле)
    country = models.CharField(_("Страна"), max_length=100)

    # Телефон клиента (необязательное поле, с валидацией по формату PHONE_VALIDATOR)
    phone = models.CharField(max_length=20, blank=True, validators=[PHONE_VALIDATOR])

    def __str__(self):
        return f"{self.name} ({self.country})" if self.country else self.name

    class Meta:
        db_table = 'clients'
        verbose_name = _("Клиент")
        verbose_name_plural = _("Клиенты")
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country']),
        ]


class Manufacturer(ReprMixin, NormalizeMixin, models.Model):
    """
    Модель производителя.
    """

    # Название производителя (обязательно и уникально)
    name = models.CharField(_("Название производителя"), max_length=150, unique=True)

    # Страна производителя (обязательное поле)
    country = models.CharField(_("Страна"), max_length=100)

    # Язык общения с производителем (необязательное поле)
    language = models.CharField(_("Язык"), max_length=50, blank=True)

    # Телефон производителя с валидацией
    phone = models.CharField(max_length=20, blank=True, validators=[PHONE_VALIDATOR])

    def __str__(self):
        return f"{self.name} ({self.country})" if self.country else self.name

    class Meta:
        db_table = 'manufacturers'
        verbose_name = _("Производитель")
        verbose_name_plural = _("Производители")
        ordering = ['name']
