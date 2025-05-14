from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.forms import UserLoginForm, UserRegistrationForm
from core.models import User
from core.services import account_activation_token


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.get_full_name(), "John Doe")
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="admin123",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)

    def test_email_normalization(self):
        user = User.objects.create_user(
            email="test@EXAMPLE.COM",
            first_name="Test",
            last_name="User",
            password="test123",
        )
        self.assertEqual(user.email, "test@example.com")

    def test_user_str(self):
        user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="test123",
        )
        self.assertEqual(str(user), "John Doe")


class UserFormsTest(TestCase):
    def test_registration_form(self):
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_email_exists(self):
        User.objects.create_user(
            email="existing@example.com",
            first_name="Existing",
            last_name="User",
            password="test123",
        )
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "existing@example.com",
            "password1": "test123",
            "password2": "test123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_login_form(self):
        user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="test123",
            is_email_verified=True,
        )
        form_data = {"email": "test@example.com", "password": "test123"}
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.user, user)

    def test_login_unverified_email(self):
        User.objects.create_user(
            email="unverified@example.com",
            first_name="Test",
            last_name="User",
            password="test123",
            is_email_verified=False,
        )
        form_data = {"email": "unverified@example.com", "password": "test123"}
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="user@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
            is_email_verified=True,
        )

    def test_register_view(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

        data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "password1": "securepassword123",
            "password2": "securepassword123",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="alice@example.com").exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_login_view(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

        data = {"email": "user@example.com", "password": "password123"}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_unauthorized(self):
        response = self.client.get(reverse("user_profile", kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_authorized(self):
        self.client.login(email="user@example.com", password="password123")
        response = self.client.get(reverse("user_profile", kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_update_profile_view(self):
        self.client.login(email="user@example.com", password="password123")
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "user@example.com",
        }
        response = self.client.post(
            reverse("user_edit", kwargs={'pk': self.user.pk}), data
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_email_verification(self):
        # Create unverified user
        user = User.objects.create_user(
            email="verify@example.com",
            first_name="Verify",
            last_name="User",
            password="test123",
            is_email_verified=False,
        )

        # Generate token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        # Verify email
        response = self.client.get(
            reverse("verify_email", kwargs={"token": token, "uidb64": uid})
        )
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)
        self.assertEqual(response.status_code, 302)

    def test_password_change(self):
        self.client.login(email="user@example.com", password="password123")
        data = {
            "old_password": "password123",
            "new_password1": "newsecurepassword123",
            "new_password2": "newsecurepassword123",
        }
        response = self.client.post(reverse("password_change"), data)
        self.assertEqual(response.status_code, 302)

        # Check new password works
        self.client.logout()
        self.assertTrue(
            self.client.login(email="user@example.com", password="newsecurepassword123")
        )


class AuthFlowTest(TestCase):
    def test_full_auth_flow(self):
        # Registration
        register_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }
        self.client.post(reverse("register"), register_data)
        user = User.objects.get(email="test@example.com")
        self.assertFalse(user.is_email_verified)

        # Email verification
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        self.client.get(reverse("verify_email", kwargs={"token": token, "uidb64": uid}))
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)

        # Login
        self.client.post(
            reverse("login"),
            {"email": "test@example.com", "password": "complexpass123"},
        )
        response = self.client.get(reverse("user_profile", kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, 200)

        # Update profile
        self.client.post(
            reverse("user_edit", kwargs={'pk': user.pk}),
            {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "test@example.com",
            },
        )
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Updated")

        # Logout
        self.client.logout()
        response = self.client.get(reverse("user_profile", kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, 302)
