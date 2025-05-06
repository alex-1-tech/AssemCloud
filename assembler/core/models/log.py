from core.models.base import _, models, ReprMixin

class ChangesLog(ReprMixin, models.Model):
    """
    Модель журнала изменений записей в базе данных.

    Эта модель используется для хранения информации о том, какие изменения
    были внесены в записи таблиц базы данных. Включает в себя название таблицы,
    идентификатор записи, изменённое поле, старое и новое значение, а также дату
    и пользователя, который произвёл изменение.
    """

    # Уникальный идентификатор записи в журнале изменений
    log_id = models.AutoField(primary_key=True)

    # Имя таблицы, в которой произошло изменение
    table_name = models.CharField(_("Имя таблицы"), max_length=100)

    # Идентификатор записи в таблице, которая была изменена
    record_id = models.BigIntegerField(_("ID записи"))

    # Имя столбца, который был изменён
    column_name = models.CharField(_("Имя столбца"), max_length=100)

    # Старое значение, которое было до изменения
    old_value = models.TextField(_("Старое значение"), blank=True, null=True)

    # Новое значение, которое было установлено
    new_value = models.TextField(_("Новое значение"), blank=True, null=True)

    # Дата и время, когда изменение было произведено
    changed_on = models.DateTimeField(_("Дата изменения"), auto_now_add=True)

    # Ссылка на пользователя, который произвёл изменение
    changed_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Пользователь, который изменил")
    )

    def __str__(self):
        return f"Change Log {self.log_id} | {self.table_name} - {self.column_name}"

    class Meta:
        db_table = 'changes_log'
        verbose_name = _("Журнал изменений")
        verbose_name_plural = _("Журналы изменений")
        ordering = ['-changed_on']
        indexes = [
            models.Index(fields=['table_name']),
            models.Index(fields=['record_id']),
            models.Index(fields=['changed_on']),
        ]
