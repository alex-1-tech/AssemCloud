from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView

from core.forms import (
    UserLoginForm,
    UserPasswordChangeForm,
    UserRegistrationForm,
    UserSetPasswordForm,
    UserUpdateForm,
)
from core.models import User
from core.services import send_verification_email, verify_email


class UserRegisterView(FormView):
    """
    Представление для регистрации пользователя 
    с использованием формы `UserRegistrationForm`.
    Отображает форму регистрации и обрабатывает её отправку.
    """

    template_name = "core/user/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("user_profile")

    def form_valid(self, form):
        """
        Если форма прошла валидацию — сохранить пользователя и продолжить обработку.
        """
        user = form.save()
        send_verification_email(user, self.request)
        messages.success(
            self.request,
            "Вы успешно зарегистрированы. \
                Подтвердите email по ссылке, отправленной на почту.",
        )
        return super().form_valid(form)


class UserLoginView(FormView):
    """
    Класс-представление для входа пользователя в систему.
    Использует форму `UserLoginForm` и метод `login` из Django.
    """

    template_name = "core/user/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("user_profile")

    def form_valid(self, form):
        """
        Если форма прошла валидацию — логинить пользователя и продолжить обработку.
        """
        user = form.user

        # Логин
        login(self.request, user)

        # Редирект
        next_url = self.request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования профиля текущего пользователя.
    Доступно только авторизованным пользователям.
    """

    model = User
    form_class = UserUpdateForm
    template_name = "core/user/edit.html"
    success_url = reverse_lazy("user_profile")

    def get_object(self, queryset=None):
        """
        Возвращает текущего пользователя вместо поиска по ID.
        """
        return self.request.user


class UserDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения профиля текущего пользователя.
    Использует DetailView, доступно только авторизованным пользователям.
    """

    model = User
    template_name = "core/user/detail.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None):
        """
        Возвращает текущего авторизованного пользователя.
        """
        return self.request.user

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex["user_roles"] = self.request.user.roles.select_related("role")
        return contex


class UserPasswordChangeView(PasswordChangeView):
    """
    Представление для смены пароля авторизованного пользователя.
    Использует стандартный PasswordChangeView с кастомной формой.
    """

    form_class = UserPasswordChangeForm
    template_name = "core/user/password_change.html"
    success_url = reverse_lazy("user_profile")

    def form_valid(self, form):
        """
        Метод вызывается при успешной валидации формы.
        Сохраняет новый пароль и вызывает logout+login при необходимости.
        """
        return super().form_valid(form)


def verify_email_view(request, uidb64, token):
    """
    Представление для верификации почты.
    """
    return verify_email(request, uidb64, token)


class ResendVerificationView(View):
    """
    Представления для повторного запроса письма верификации почты.
    """

    def get(self, request):
        return render(request, "core/user/resend_verification.html")

    def post(self, request):
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
    form_class = UserSetPasswordForm
