from django.views.generic.edit import FormView, UpdateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from core.models import User
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.forms import (
    UserRegistrationForm, UserLoginForm, UserUpdateForm, UserPasswordChangeForm
)

class UserRegisterView(FormView):
    """
    Представление для регистрации пользователя с использованием формы `UserRegistrationForm`.
    Отображает форму регистрации и обрабатывает её отправку.
    """
    template_name = "core/user/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("user_profile")

    def form_valid(self, form):
        """
        Если форма прошла валидацию — сохранить пользователя и продолжить обработку.
        """
        form.save()
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
        login(self.request, form.user)
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
