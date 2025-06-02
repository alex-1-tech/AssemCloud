"""User management views.

It consists of registration, login, profile editing,
password change and email confirmation.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView

from core.forms import (
    UserLoginForm,
    UserPasswordChangeForm,
    UserRegistrationForm,
    UserSetPasswordForm,
    UserUpdateForm,
)
from core.models import Task, User
from core.services import send_verification_email, verify_email


class UserRegisterView(FormView):
    """Handles new user registration."""

    template_name = "core/user/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form: UserRegistrationForm) -> HttpResponseRedirect:
        """Save new user and sends verification email."""
        user = form.save()
        send_verification_email(user, self.request)
        messages.success(
            self.request,
            "Вы успешно зарегистрированы. \
                Подтвердите email по ссылке, отправленной на почту.",
        )
        return super().form_valid(form)


class UserLoginView(FormView):
    """Handles user login via login form."""

    template_name = "core/user/login.html"
    form_class = UserLoginForm

    def form_valid(self, form: UserLoginForm) -> HttpResponseRedirect:
        """Log in the user and redirects to the appropriate page."""
        user = form.user
        login(self.request, user)

        next_url = self.request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Return URL for redirection after login."""
        return reverse_lazy("user_profile", kwargs={"pk": self.request.user.pk})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Allows users or directors to edit profiles."""

    model = User
    form_class = UserUpdateForm
    template_name = "core/user/edit.html"

    def get_object(self) -> User:
        """Return the user object for editing. Only directors can edit others."""
        user_pk = self.kwargs.get("pk")
        user_to_edit = get_object_or_404(User, pk=user_pk)
        is_director = self.request.user.roles.filter(role__name="Директор").exists()

        if self.request.user.pk != user_to_edit.pk and not is_director:
            raise PermissionDenied
        return user_to_edit

    def get_success_url(self) -> str:
        """Return profile URL after successful update."""
        return reverse_lazy("user_profile", kwargs={"pk": self.request.user.pk})


class UserListView(ListView):
    """Displays a list of all users (only for directors)."""

    model = User
    template_name = "core/list.html"
    context_object_name = "users"

    def get_context_data(self, **kwargs: object) -> dict:
        """Add formatted user list to context for rendering."""
        context = super().get_context_data(**kwargs)

        if not self.request.user.roles.filter(role__name="Директор").exists():
            raise PermissionDenied

        items = [
            {
                "title": user.email,
                "subtitle": f"{user.first_name} {user.last_name}",
                "view_url": reverse("user_profile", args=[user.pk]),
                "edit_url": reverse("user_edit", args=[user.pk]),
            }
            for user in context["users"]
        ]

        context.update({
            "title": "Пользователи",
            "items": items,
        })
        context["user_roles"] = list(
            self.request.user.roles.values_list("role__name", flat=True),
        )
        return context

    def get_queryset(self) -> object:
        """Return a queryset of users filtered by the search query."""
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(email__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q),
            )
        return qs


class UserDetailView(LoginRequiredMixin, DetailView):
    """Displays detailed user profile."""

    model = User
    template_name = "core/user/detail.html"
    context_object_name = "user_profile"

    def get_object(self) -> User:
        """Return the user to be displayed. Only directors can view others."""
        user_pk = self.kwargs.get("pk")
        user_to_edit = get_object_or_404(User, pk=user_pk)
        is_director = self.request.user.roles.filter(role__name="Директор").exists()

        if self.request.user.pk != user_to_edit.pk and not is_director:
            raise PermissionDenied
        return user_to_edit

    def get_context_data(self, **kwargs: object) -> dict:
        """Add user roles to context."""
        context = super().get_context_data(**kwargs)
        user = self.object

        context["user_profile"] = user
        context["user_roles"] = user.roles.select_related("role")
        context["user_tasks"] = Task.objects.filter(
            recipient=user,
        ).select_related("sender").order_by("-due_date")
        return context


class UserPasswordChangeView(PasswordChangeView):
    """Handles password change for authenticated users."""

    form_class = UserPasswordChangeForm
    template_name = "core/user/password_change.html"

    def form_valid(self, form: UserPasswordChangeForm) -> HttpResponseRedirect:
        """Process valid password change form."""
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Return URL after successful password change."""
        return reverse_lazy("user_profile", kwargs={"pk": self.request.user.pk})


def verify_email_view(
        request: HttpRequest, uidb64: str, token: str,
    ) -> HttpResponseRedirect:
    """Handle email verification via link from email."""
    return verify_email(request, uidb64, token)


class ResendVerificationView(View):
    """Allows resending of verification email."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render resend verification form."""
        return render(request, "core/user/resend_verification.html")

    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        """Handle verification email resend request."""
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            if user.is_email_verified:
                messages.info(request, "Email уже подтверждён.")
            else:
                send_verification_email(user, request)
                messages.success(request, "Письмо отправлено повторно.")
        else:
            messages.error(request, "Пользователь с таким email не найден.")
        return redirect("login")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Handles password reset confirmation via email link."""

    form_class = UserSetPasswordForm
