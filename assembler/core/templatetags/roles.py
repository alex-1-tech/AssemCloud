"""Module for creating a role confirmation filter."""

from django import template

register = template.Library()


@register.filter
def has_any_role(user_roles: list[str], roles_str: str) -> bool:
    """Check if a person has a suitable role."""
    if not user_roles:
        return False
    roles = [r.strip() for r in str(roles_str).split(",")]
    return any(role in user_roles for role in roles)
