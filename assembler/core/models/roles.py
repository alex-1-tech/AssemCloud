from core.models.base import _, models, NormalizeMixin, ReprMixin
from core.models.user import User

class Role(ReprMixin, NormalizeMixin, models.Model):
    """
    Модель для хранения ролей пользователей.
    """
    name = models.CharField(_("Название роли"), max_length=50, unique=True)
    description = models.TextField(_("Описание роли"), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roles'
        verbose_name = _('Роль')
        verbose_name_plural = _('Роли')
        ordering = ['name']


class UserRole(ReprMixin, models.Model):
    """
    Модель для связывания пользователей с их ролями.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    role_description = models.TextField(_("Индивидуальное описание роли"), blank=True)

    class Meta:
        db_table = 'user_roles'
        verbose_name = _("Роль пользователя")
        verbose_name_plural = _("Роли пользователей")
        constraints = [
            models.UniqueConstraint(fields=['user', 'role'], name='unique_user_role')
        ]

    def __str__(self):
        return f"{self.user} — {self.role}"
