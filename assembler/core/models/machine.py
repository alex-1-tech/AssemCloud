from core.models.base import NormalizeMixin, ReprMixin, _, models
from core.models.client import Client


class Machine(ReprMixin, NormalizeMixin, models.Model):
    """
    Модель для хранения информации о машинах.

    Эта модель предназначена для хранения данных о машинах, включая название,
    версию и клиентов, с которыми связана машина. Также есть возможность
    добавлять несколько клиентов для каждой машины через промежуточную модель.
    """

    # Название машины (обязательное поле)
    name = models.CharField(_("Название машины"), max_length=255)

    # Версия машины (обязательное поле)
    version = models.CharField(_("Версия машины"), max_length=50)

    # Множество клиентов, связанных с данной машиной. Используется промежуточная модель MachineClient.
    clients = models.ManyToManyField(
        Client,
        through="MachineClient",
        related_name="machines",
        verbose_name=_("Клиент"),
    )

    def __str__(self):
        return f"{self.name} #{self.pk} — Версия {self.version or 'N/A'}"

    class Meta:
        db_table = "machines"
        verbose_name = _("Машина")
        verbose_name_plural = _("Машины")
        constraints = [
            models.UniqueConstraint(
                fields=["name", "version"], name="unique_name_per_version"
            )
        ]


class MachineClient(ReprMixin, models.Model):
    """
    Промежуточная модель для связи между Машинами и Клиентами.

    Эта модель представляет собой связь между машиной и клиентом, позволяя одной
    машине быть связанной с несколькими клиентами. Также поддерживается возможность
    добавления комментариев и отслеживания даты добавления записи.
    """

    # Ссылка на модель машины
    machine = models.ForeignKey(
        Machine, on_delete=models.CASCADE, verbose_name=_("Машина")
    )

    # Ссылка на модель клиента
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name=_("Клиент")
    )

    # Дата и время добавления этой связи
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Дата добавления")
    )

    # Комментарий, который можно оставить к связи
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))

    def __str__(self):
        return f"{self.client} <-> {self.machine}"

    class Meta:
        db_table = "machine_clients"
        verbose_name = _("Связь Машина-Клиент")
        verbose_name_plural = _("Связи Машина-Клиент")
        unique_together = ("machine", "client")
