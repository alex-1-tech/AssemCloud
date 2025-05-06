from core.models.base import _, models, ReprMixin


class ChangesLog(ReprMixin, models.Model):
    """
    Журнал изменений записей в базе данных.
    """
    log_id = models.AutoField(primary_key=True)
    table_name = models.CharField(_("Имя таблицы"), max_length=100)
    record_id = models.PositiveIntegerField(_("ID записи"))
    column_name = models.CharField(_("Имя столбца"), max_length=100)
    old_value = models.TextField(_("Старое значение"), blank=True, null=True)
    new_value = models.TextField(_("Новое значение"), blank=True, null=True)
    changed_on = models.DateTimeField(_("Дата изменения"), auto_now_add=True)
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
