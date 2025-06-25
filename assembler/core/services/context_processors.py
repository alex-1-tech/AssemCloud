"""Module provides context processors.

Need to determine if the current authenticated user has the 'Director' role,
and generally if the user has any roles assigned.
The `is_director` and `is_role` functions return dictionaries indicating
the user's role status for use in templates.
"""

from django.http import HttpRequest


def is_director(request: HttpRequest) -> dict[str, bool]:
    """Context processor to check if the current user has the 'Director' role."""
    if request.user.is_authenticated:
        return {
            "is_director": request.user.roles.filter(role__name="Директор").exists(),
        }
    return {"is_director": False}


def is_role(request: HttpRequest) -> dict[str, bool]:
    """Context processor to check if the current user has any role assigned."""
    if request.user.is_authenticated:
        return {
            "is_user": request.user.roles.exists(),
        }
    return {"is_user": False}
