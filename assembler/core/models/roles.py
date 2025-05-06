from core.models.base import _, models, NormalizeMixin, ReprMixin
from core.models.user import User

class Role(ReprMixin, NormalizeMixin, models.Model):
    """
    Модель для хранения ролей пользователей.

    Эта модель описывает роли, которые могут быть назначены пользователям в системе.
    Роли могут включать информацию о названии и описание, что помогает системно
    классифицировать права доступа и обязанности пользователей.
    """
    
    # Название роли (уникальное).
    name = models.CharField(_("Название роли"), max_length=50, unique=True)
    
    # Описание роли (необязательное поле).
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

    Эта модель служит для создания связи между пользователем и его ролью.
    Каждому пользователю может быть назначено несколько ролей, и каждая роль
    может быть описана индивидуально для пользователя.
    """

    # Связь с моделью 'User', указывающая, какой пользователь имеет эту роль.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    
    # Связь с моделью 'Role', указывающая, какую роль имеет пользователь.
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    
    # Описание роли для конкретного пользователя (необязательное поле).
    role_description = models.TextField(_("Индивидуальное описание роли"), blank=True)

    def __str__(self):
        return f"{self.user} — {self.role}"

    class Meta:
        db_table = 'user_roles'
        verbose_name = _("Связь Роль-Пользователь")
        verbose_name_plural = _("Связи Роль-Пользователь")
        constraints = [
            models.UniqueConstraint(fields=['user', 'role'], name='unique_user_role')
        ]
