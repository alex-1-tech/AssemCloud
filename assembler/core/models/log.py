"""Model for tracking changes to database records.

This module defines the `ChangesLog` model used for recording modifications made to
database entries. It logs which table and record were modified, what field was changed,
its old and new values, the user responsible for the change, and when it occurred.
"""

from typing import ClassVar

from core.models.base import ReprMixin, _, models


class ChangesLog(ReprMixin, models.Model):
    """Model representing a single change log entry for database auditing.

    This model captures changes made to specific fields of a record in any table.
    It stores the table name, record ID, the field that changed, old and new values,
    the timestamp of the change, and the user who made the change.
    """

    log_id = models.AutoField(
        primary_key=True,
        verbose_name=_("Идентификатор лога"),
    )

    table_name = models.CharField(
        _("Имя таблицы"),
        max_length=100,
        help_text=_("Название таблицы, в которой произошло изменение"),
    )

    record_id = models.BigIntegerField(
        _("ID записи"),
        help_text=_("Идентификатор измененной записи"),
    )

    column_name = models.CharField(
        _("Имя столбца"),
        max_length=100,
        help_text=_("Название поля, которое было изменено"),
    )

    old_value = models.TextField(
        _("Старое значение"),
        blank=True,
        null=True,
        help_text=_("Значение до изменения"),
    )

    new_value = models.TextField(
        _("Новое значение"),
        blank=True,
        null=True,
        help_text=_("Значение после изменения"),
    )

    changed_on = models.DateTimeField(
        _("Дата изменения"),
        auto_now_add=True,
        help_text=_("Время, когда было произведено изменение"),
    )

    changed_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Пользователь, который изменил"),
        help_text=_("Пользователь, выполнивший изменение"),
    )

    def __str__(self) -> str:
        """Return a human-readable summary of the change log entry."""
        return f"Change Log {self.log_id} | {self.table_name} - {self.column_name}"

    class Meta:
        """Model metadata: table name, verbose names, ordering, and indexes."""

        db_table: ClassVar[str] = "changes_log"
        verbose_name: ClassVar[str] = _("Журнал изменений")
        verbose_name_plural: ClassVar[str] = _("Журналы изменений")
        ordering: ClassVar[list[str]] = ["-changed_on"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["table_name"]),
            models.Index(fields=["record_id"]),
            models.Index(fields=["changed_on"]),
        ]
