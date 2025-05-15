"""Forms for user.

Forms registration, authentication, profile update,
and password management in the core app.

Includes:
- UserRegistrationForm: for registering new users with email, name,
    phone, address, and password.
- UserLoginForm: for authenticating users by email and password.
- UserUpdateForm: for updating user profile fields.
- UserPasswordChangeForm: for authenticated users to change their password.
- UserSetPasswordForm: for setting a new password after password reset.
"""
from typing import Any

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from core.models import User


class UserRegistrationForm(forms.ModelForm):
    """Form for registering a new user.

    Fields:
    - email (unique identifier/login)
    - first name and last name
    - phone and address (optional)
    - password and password confirmation
    """

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput,
    )

    class Meta:
        """Model metadata for Blueprint."""

        model = User
        fields = ("first_name", "last_name", "email", "phone", "address")

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize the form with placeholders and CSS classes for fields."""
        super().__init__(*args, **kwargs)

        placeholders = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "example@mail.com",
            "phone": "+79991234567",
            "address": "Your address",
            "password1": "Enter password",
            "password2": "Repeat password",
        }
        for name, text in placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs["placeholder"] = text

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_email(self) -> str:
        """Validate that the email is unique.

        Raises ValidationError if a user with this email already exists.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with this email already exists."))
        return email

    def clean_password1(self) -> str:
        """Validate the strength of the password using Django's validators."""
        password = self.cleaned_data.get("password1")
        validate_password(password)
        return password

    def clean(self) -> dict[str, Any]:
        """Validate that both password fields match.

        Adds an error to password2 if they do not match.
        """
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", _("Passwords do not match."))
        return cleaned_data

    def save(self, *, commit: bool = True) -> User:
        """Save the user instance with a hashed password.

        Sets the password to the value of password1 and saves if commit=True.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """Form for user login by email and password.

    Authenticates credentials via `authenticate`.
    """

    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "example@mail.com",
            },
        ),
    )

    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password",
            },
        ),
    )

    def clean(self) -> dict[str, Any]:
        """Validate login credentials.

        Checks if the email and password are correct, and if the email is verified.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError(_("Invalid email or password."))

            if not getattr(user, "is_email_verified", False):
                raise forms.ValidationError(
                    _("Email is not verified. Please check your inbox."),
                )

            self.user = user
        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    """Form for updating user profile.

    Allows editing of first name, last name, email, phone, and address.
    """

    class Meta:
        """Model metadata for UserUpdateForm."""

        model = User
        fields = ("first_name", "last_name", "email", "phone", "address")

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize the form with placeholders and CSS classes for fields."""
        super().__init__(*args, **kwargs)

        placeholders = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "example@mail.com",
            "phone": "+79991234567",
            "address": "Your address",
        }
        for name, text in placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs["placeholder"] = text

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_email(self) -> str:
        """Validate that the updated email is unique.

        Excludes the current user instance from the uniqueness check.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("A user with this email already exists."))
        return email


class UserPasswordChangeForm(PasswordChangeForm):
    """Form for authenticated users to change their password.

    Extends Django's PasswordChangeForm with custom labels and placeholders.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize form fields with labels, placeholders, and CSS classes."""
        super().__init__(*args, **kwargs)

        labels = {
            "old_password": _("Old Password"),
            "new_password1": _("New Password"),
            "new_password2": _("Confirm New Password"),
        }

        placeholders = {
            "old_password": _("Enter current password"),
            "new_password1": _("New password"),
            "new_password2": _("Confirm new password"),
        }

        for name, placeholder in placeholders.items():
            self.fields[name].label = labels.get(name, self.fields[name].label)
            self.fields[name].widget.attrs.update(
                {"class": "form-control", "placeholder": placeholder},
            )


class UserSetPasswordForm(SetPasswordForm):
    """Form for setting a new password after a password reset.

    Extends Django's SetPasswordForm with custom labels and placeholders.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize form fields with labels, placeholders, and CSS classes."""
        super().__init__(*args, **kwargs)

        labels = {
            "new_password1": _("New Password"),
            "new_password2": _("Confirm New Password"),
        }

        placeholders = {
            "new_password1": _("Enter new password"),
            "new_password2": _("Repeat new password"),
        }

        for name, placeholder in placeholders.items():
            self.fields[name].label = labels.get(name)
            self.fields[name].widget.attrs.update(
                {"class": "form-control", "placeholder": placeholder},
            )
