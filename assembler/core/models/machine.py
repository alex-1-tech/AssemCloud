from core.models.base import _, models, NormalizeMixin, ReprMixin
from core.models.client import Client


class Machine(ReprMixin, NormalizeMixin, models.Model):
    """
    Модель для хранения информации о машинах.
    """
    name = models.CharField(_("Название машины"), max_length=255)
    version = models.CharField(_("Версия машины"), max_length=50, blank=True)
    clients = models.ManyToManyField(Client, through='MachineClient', related_name='machines', verbose_name=_("Клиент"))

    def __str__(self):
        name = self.name if self.name else _('Без названия')
        version = self.version if self.version else _('нет')
        return f"{name} (version: {version})"
    
    class Meta:
        db_table = 'machines'
        verbose_name = _('Машина')
        verbose_name_plural = _('Машины')
        constraints = [
            models.UniqueConstraint(
                fields=["name", "version"],
                name='unique_name_per_version'
            )
        ]

class MachineClient(ReprMixin, models.Model):
    """
    Промежуточная модель для связи между Машинами и Клиентами.
    """
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, verbose_name=_("Машина"))
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name=_("Клиент"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата добавления"))
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))

    def __str__(self):
        return f"{self.client} <-> {self.machine}"

    class Meta:
        db_table = 'machine_clients'
        verbose_name = _("Связь Машина-Клиент")
        verbose_name_plural = _("Связи Машина-Клиент")
        unique_together = ('machine', 'client')
