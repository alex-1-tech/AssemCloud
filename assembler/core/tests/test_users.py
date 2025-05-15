"""Test suite.

For User model, forms, views, and authentication flow in the core app.
"""

import secrets

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.forms import UserLoginForm, UserRegistrationForm
from core.models import User
from core.services import account_activation_token


class UserModelTest(TestCase):
    """Tests for User model creation and behavior."""

    def setUp(self) -> None:
        """Set up passwords for test users."""
        self.default_password = secrets.token_urlsafe(12)
        self.new_password = secrets.token_urlsafe(12)

    def test_create_user(self) -> None:
        """Create a regular user and verify attributes."""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password=self.default_password,
        )
        self.assertEqual(user.email, "test@example.com")  # noqa: PT009
        self.assertEqual(user.get_full_name(), "John Doe")  # noqa: PT009
        self.assertFalse(user.is_staff)  # noqa: PT009
        self.assertTrue(user.is_active)  # noqa: PT009
        self.assertFalse(user.is_superuser)  # noqa: PT009

    def test_create_superuser(self) -> None:
        """Create a superuser and verify privileges."""
        admin = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password=self.default_password,
        )
        self.assertTrue(admin.is_staff)  # noqa: PT009
        self.assertTrue(admin.is_superuser)  # noqa: PT009
        self.assertTrue(admin.is_active)  # noqa: PT009

    def test_email_normalization(self) -> None:
        """Emails are normalized to lowercase on creation."""
        user = User.objects.create_user(
            email="TEST@Example.COM",
            first_name="Test",
            last_name="User",
            password=self.default_password,
        )
        self.assertEqual(user.email, "test@example.com")  # noqa: PT009

    def test_user_str(self) -> None:
        """String representation returns full name."""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password=self.default_password,
        )
        self.assertEqual(str(user), "John Doe")  # noqa: PT009


class UserFormsTest(TestCase):
    """Tests for user registration and login forms."""

    def setUp(self) -> None:
        """Set up default password for forms tests."""
        self.default_password = secrets.token_urlsafe(12)

    def test_registration_form_valid(self) -> None:
        """Registration form with valid data should be valid."""
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password1": self.default_password,
            "password2": self.default_password,
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())  # noqa: PT009

    def test_registration_form_email_exists(self) -> None:
        """Registration form with duplicate email should be invalid."""
        User.objects.create_user(
            email="existing@example.com",
            first_name="Existing",
            last_name="User",
            password=self.default_password,
        )
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "existing@example.com",
            "password1": self.default_password,
            "password2": self.default_password,
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())  # noqa: PT009
        self.assertIn("email", form.errors)  # noqa: PT009

    def test_login_form_valid(self) -> None:
        """Login form with verified email should be valid."""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password=self.default_password,
            is_email_verified=True,
        )
        form_data = {"email": "test@example.com", "password": self.default_password}
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())  # noqa: PT009
        self.assertEqual(form.user, user)  # noqa: PT009

    def test_login_unverified_email(self) -> None:
        """Login should fail if the email is not verified."""
        User.objects.create_user(
            email="unverified@example.com",
            first_name="Test",
            last_name="User",
            password=self.default_password,
            is_email_verified=False,
        )
        form_data = {
            "email": "unverified@example.com",
            "password": self.default_password,
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())  # noqa: PT009
        self.assertIn("__all__", form.errors)  # noqa: PT009


class UserViewsTest(TestCase):
    """Tests for user-related views and their responses."""

    def setUp(self) -> None:
        """Set up client, user, and passwords for views tests."""
        self.client = Client()
        self.default_password = secrets.token_urlsafe(12)
        self.new_password = secrets.token_urlsafe(12)
        self.user = User.objects.create_user(
            email="user@example.com",
            first_name="John",
            last_name="Doe",
            password=self.default_password,
            is_email_verified=True,
        )

    def test_register_view_get(self) -> None:
        """GET request to register view returns status 200."""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)  # noqa: PT009

    def test_register_view_post(self) -> None:
        """POST valid registration data redirects and sends verification email."""
        data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "password1": self.default_password,
            "password2": self.default_password,
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 302)  # noqa: PT009
        self.assertTrue(User.objects.filter(email="alice@example.com").exists())  # noqa: PT009
        self.assertEqual(len(mail.outbox), 1)  # noqa: PT009

    def test_login_view_get(self) -> None:
        """GET request to login view returns status 200."""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)  # noqa: PT009

    def test_login_view_post(self) -> None:
        """POST valid login credentials redirects successfully."""
        data = {"email": "user@example.com", "password": self.default_password}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 302)  # noqa: PT009

    def test_profile_view_unauthorized(self) -> None:
        """Unauthenticated users are redirected from profile page."""
        response = self.client.get(reverse("user_profile", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 302)  # noqa: PT009

    def test_profile_view_authorized(self) -> None:
        """Authenticated users can access their profile page."""
        login_successful = self.client.login(
            email="user@example.com", password=self.default_password,
        )
        self.assertTrue(login_successful)  # noqa: PT009
        response = self.client.get(reverse("user_profile", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)  # noqa: PT009

    def test_update_profile_view(self) -> None:
        """Authenticated user can update their profile."""
        login_successful = self.client.login(
            email="user@example.com", password=self.default_password,
        )
        self.assertTrue(login_successful)  # noqa: PT009
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "user@example.com",
        }
        response = self.client.post(
            reverse("user_edit", kwargs={"pk": self.user.pk}), data,
        )
        self.assertEqual(response.status_code, 302)  # noqa: PT009
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")  # noqa: PT009

    def test_email_verification(self) -> None:
        """Email verification activates the user`s account."""
        user = User.objects.create_user(
            email="verify@example.com",
            first_name="Verify",
            last_name="User",
            password=self.default_password,
            is_email_verified=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        response = self.client.get(
            reverse("verify_email", kwargs={"token": token, "uidb64": uid}),
        )
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)  # noqa: PT009
        self.assertEqual(response.status_code, 302)  # noqa: PT009

    def test_password_change(self) -> None:
        """User can change password and log in with new password."""
        login_successful = self.client.login(
            email="user@example.com", password=self.default_password,
        )
        self.assertTrue(login_successful)  # noqa: PT009
        data = {
            "old_password": self.default_password,
            "new_password1": self.new_password,
            "new_password2": self.new_password,
        }
        response = self.client.post(reverse("password_change"), data)
        self.assertEqual(response.status_code, 302)  # noqa: PT009

        self.client.logout()
        login_with_new_password = self.client.login(
            email="user@example.com", password=self.new_password,
        )
        self.assertTrue(login_with_new_password)  # noqa: PT009


class AuthFlowTest(TestCase):
    """End-to-end authentication flow testing."""

    def setUp(self) -> None:
        """Set up client and password for auth flow tests."""
        self.client = Client()
        self.default_password = secrets.token_urlsafe(12)

    def test_full_auth_flow(self) -> None:
        """Register, verify email, login, update profile, logout."""
        register_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": self.default_password,
            "password2": self.default_password,
        }
        self.client.post(reverse("register"), register_data)
        user = User.objects.get(email="test@example.com")
        self.assertFalse(user.is_email_verified)  # noqa: PT009

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        self.client.get(reverse("verify_email", kwargs={"token": token, "uidb64": uid}))
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)  # noqa: PT009

        self.client.post(
            reverse("login"),
            {
                "email": "test@example.com",
                "password": self.default_password,
            },
        )
        response = self.client.get(reverse("user_profile", kwargs={"pk": user.pk}))
        self.assertEqual(response.status_code, 200)  # noqa: PT009

        self.client.post(
            reverse("user_edit", kwargs={"pk": user.pk}),
            {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "test@example.com",
            },
        )
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Updated")  # noqa: PT009

        self.client.logout()
        response = self.client.get(reverse("user_profile", kwargs={"pk": user.pk}))
        self.assertEqual(response.status_code, 302)  # noqa: PT009
