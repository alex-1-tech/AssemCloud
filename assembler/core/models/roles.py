"""Role and UserRole models for user role management in the core app.

This module defines Role and UserRole models for assigning and managing
user roles within the system. Roles include a name and optional description,
and UserRole links users to their assigned roles with optional custom descriptions.
"""

from typing import ClassVar

from core.models.base import NormalizeMixin, ReprMixin, _, models
from core.models.user import User


class Role(ReprMixin, NormalizeMixin, models.Model):
    """Model to store user roles.

    Roles represent classifications of user permissions and responsibilities
    within the system. Each role has a unique name and an optional description.
    """

    name: str = models.CharField(
        _("Role name"),
        max_length=50,
        unique=True,
    )
    description: str = models.TextField(
        _("Role description"),
        blank=True,
    )

    def __str__(self) -> str:
        """Return the role's name as its string representation."""
        return self.name

    class Meta:
        """Meta information for Role model."""

        db_table: ClassVar[str] = "roles"
        verbose_name: ClassVar[str] = _("Role")
        verbose_name_plural: ClassVar[str] = _("Roles")
        ordering: ClassVar[list[str]] = ["name"]


class UserRole(ReprMixin, models.Model):
    """Model linking users to their roles.

    Represents the many-to-many relationship between users and roles.
    Each user can have multiple roles, with an optional individual description
    for each user-role assignment.
    """

    user: User = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="roles",
    )
    role: Role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="users",
    )
    role_description: str = models.TextField(
        _("Individual role description"),
        blank=True,
    )

    def __str__(self) -> str:
        """Return a string showing the user and their role."""
        return f"{self.user} — {self.role}"

    class Meta:
        """Meta information for UserRole model."""

        db_table: ClassVar[str] = "user_roles"
        verbose_name: ClassVar[str] = _("User-Role Link")
        verbose_name_plural: ClassVar[str] = _("User-Role Links")
        constraints: ClassVar[list[object]] = [
            models.UniqueConstraint(fields=["user", "role"], name="unique_user_role"),
        ]
