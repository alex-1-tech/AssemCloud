"""Middleware to track the current authenticated user per request."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

_user: threading.local = threading.local()


def get_current_user() -> object | None:
    """Retrieve the current authenticated user stored in thread-local storage."""
    return getattr(_user, "value", None)


class CurrentUserMiddleware:
    """Middleware to set the current authenticated user into thread-local storage."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware with the given response handler."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the incoming request and store the current user.

        If the user is authenticated, it is stored in thread-local storage.
        """
        _user.value = request.user if request.user.is_authenticated else None
        return self.get_response(request)
