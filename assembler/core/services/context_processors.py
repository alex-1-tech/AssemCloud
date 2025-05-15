"""Module provides a context processor.

Need to determineif the current authenticated user has the 'Director' role.
The `is_director` function returns a dictionary indicating the user's role
status for use in templates.
"""
from django.http import HttpRequest


def is_director(request: HttpRequest) -> dict[str, bool]:
    """Context processor to check if the current user has the 'Director' role."""
    if request.user.is_authenticated:
        return {
            "is_director": request.user.roles.filter(role__name="Директор").exists(),
        }
    return {"is_director": False}
