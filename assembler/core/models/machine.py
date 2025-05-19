"""Models for storing machines and their associations with clients.

This module defines the `Machine` model representing individual machines
and the `MachineClient` intermediary model that links machines to clients.

Each machine can be associated with multiple clients using a many-to-many
relationship managed through `MachineClient`, which also allows for adding
comments and tracking the creation date of each link.
"""

from typing import ClassVar

from core.models.base import NormalizeMixin, ReprMixin, _, models
from core.models.client import Client


class Machine(ReprMixin, NormalizeMixin, models.Model):
    """Model representing a machine with a name, version, and associated clients.

    Each machine can be linked to multiple clients via the `MachineClient` model.
    """

    name = models.CharField(
        _("Название машины"),
        max_length=255,
        blank=False,
        null=False,
    )

    version = models.CharField(
        _("Версия машины"),
        max_length=50,
        blank=False,
        null=False,
    )

    clients = models.ManyToManyField(
        Client,
        through="MachineClient",
        related_name="machines",
        verbose_name=_("Клиент"),
    )

    def __str__(self) -> str:
        """Return string representation of the machine with name and version."""
        return f"{self.name} #{self.pk} — Версия {self.version or 'N/A'}"

    class Meta:
        """Model metadata: database table name, verbose names and constraints."""

        db_table: ClassVar[str] = "machines"
        verbose_name: ClassVar[str] = _("Машина")
        verbose_name_plural: ClassVar[str] = _("Машины")
        constraints: ClassVar[list[models.UniqueConstraint]] = [
            models.UniqueConstraint(
                fields=["name", "version"],
                name="unique_name_per_version",
            ),
        ]


class MachineClient(ReprMixin, models.Model):
    """Intermediary model linking machines to clients with metadata.

    This model enables a many-to-many relationship between `Machine` and `Client`
    and supports additional fields like comments and creation date.
    """

    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        verbose_name=_("Машина"),
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name=_("Клиент"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата добавления"),
    )

    comment = models.TextField(
        blank=True,
        verbose_name=_("Комментарий"),
    )

    def __str__(self) -> str:
        """Return a string showing the client-machine association."""
        return f"{self.client} <-> {self.machine}"

    class Meta:
        """Model metadata: database table name, verbose names and unique constraint."""

        db_table: ClassVar[str] = "machine_clients"
        verbose_name: ClassVar[str] = _("Связь Машина-Клиент")
        verbose_name_plural: ClassVar[str] = _("Связи Машина-Клиент")
        unique_together: ClassVar[tuple[str, str]] = ("machine", "client")
