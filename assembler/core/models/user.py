"""Custom user model and manager definitions for the core app.

This module defines a custom user model that uses email as the unique identifier
and includes additional fields such as phone, address, and email verification status.
It also provides a custom user manager for creating users and superusers.
"""
from __future__ import annotations

from typing import ClassVar

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    PermissionsMixin,
)
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models.base import PHONE_VALIDATOR, NormalizeMixin, ReprMixin, normalize_email


class UserManager(BaseUserManager):
    """Manager for creating users and superusers.

    Overrides standard methods to handle user creation using email as the unique
    identifier along with other custom fields.
    """

    def create_user(
        self, email: str, password: str|None = None, **extra_fields: object,
    ) -> User:
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError(_("Email must be provided"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str|None = None, **extra_fields: object,
    ) -> User:
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser must have is_staff=True."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(ReprMixin, NormalizeMixin, AbstractBaseUser, PermissionsMixin):
    """Custom user model with extended fields and email as username.

    Extends Django's AbstractBaseUser and PermissionsMixin to use email as
    the unique identifier instead of username. Adds fields such as first and last name,
    phone, address, and email verification status.
    """

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        related_query_name="custom_user",
        blank=True,
        help_text=_("Groups the user belongs to."),
        verbose_name=_("groups"),
    )

    first_name = models.CharField(_("First name"), max_length=100)
    last_name = models.CharField(_("Last name"), max_length=100)
    email = models.EmailField(_("Email"), unique=True, blank=False, null=False)
    phone = models.CharField(
        _("Phone"),
        max_length=20,
        blank=True,
        validators=[PHONE_VALIDATOR],
    )
    address = models.TextField(_("Address"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    is_staff = models.BooleanField(_("Staff"), default=False)
    date_joined = models.DateTimeField(_("Date joined"), default=timezone.now)
    is_email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = ["first_name", "last_name"]

    def __str__(self) -> str:
        """Return the user's full name as a string representation."""
        return f"{self.first_name} {self.last_name}"

    def save(self, *args: object, **kwargs: object) -> None:
        """Override save to normalize email before saving."""
        if self.email:
            self.email = normalize_email(self.email)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Return the absolute URL to the user's profile page."""
        return reverse("user_detail", kwargs={"pk": self.pk})

    def get_full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        """Return the user's short name (first name or email as fallback)."""
        return self.first_name or self.email or ""

    class Meta:
        """Model metadata: database table name, verbose names, and app label."""

        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        app_label = "core"
