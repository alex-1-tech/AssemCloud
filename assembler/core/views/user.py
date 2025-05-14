from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView
from django.core.exceptions import PermissionDenied
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
    success_url = reverse_lazy("login")

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

    def form_valid(self, form):
        """
        Если форма прошла валидацию — логинить пользователя и продолжить обработку.
        """
        user = form.user

        login(self.request, user)

        next_url = self.request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Перенаправление на страницу профиля пользователя после успешного логина.
        """
        return reverse_lazy('user_profile', kwargs={'pk': self.request.user.pk})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования профиля.
    Пользователь может редактировать только себя.
    Директор может редактировать любого.
    """

    model = User
    form_class = UserUpdateForm
    template_name = "core/user/edit.html"

    def get_object(self, queryset=None):
        """
        Возвращает пользователя, профиль которого мы хотим изменить.
        Если передан pk в URL, ищем этого пользователя.
        """
        user_pk = self.kwargs.get('pk')
        user_to_edit = get_object_or_404(User, pk=user_pk)
        is_director = self.request.user.roles.filter(role__name="Директор").exists()

        if self.request.user.pk != user_to_edit.pk and not is_director:
            raise PermissionDenied("Вы не можете редактировать чужой профиль.")
        return user_to_edit

    def get_success_url(self):
        """
        Перенаправление на страницу профиля пользователя после успешного логина.
        """
        return reverse_lazy('user_profile', kwargs={'pk': self.request.user.pk})

class UserListView(ListView):
    model = User
    template_name = "core/list.html"
    context_object_name = "users"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if not self.request.user.roles.filter(role__name="Директор").exists():
            raise PermissionDenied("У вас нет доступа к списку пользователей.")

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
        
        return context
    
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
        Возвращает пользователя, профиль которого мы хотим отобразить.
        Если передан pk в URL, ищем этого пользователя.
        """
        user_pk = self.kwargs.get('pk')
        user_to_edit = get_object_or_404(User, pk=user_pk)
        is_director = self.request.user.roles.filter(role__name="Директор").exists()

        if self.request.user.pk != user_to_edit.pk and not is_director:
            raise PermissionDenied("Вы не можете редактировать чужой профиль.")
        return user_to_edit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_roles"] = self.object.roles.select_related("role")
        return context


class UserPasswordChangeView(PasswordChangeView):
    """
    Представление для смены пароля авторизованного пользователя.
    Использует стандартный PasswordChangeView с кастомной формой.
    """

    form_class = UserPasswordChangeForm
    template_name = "core/user/password_change.html"

    def form_valid(self, form):
        """
        Метод вызывается при успешной валидации формы.
        Сохраняет новый пароль и вызывает logout+login при необходимости.
        """
        return super().form_valid(form)
    
    def get_success_url(self):
        """
        Перенаправление на страницу профиля пользователя после успешного логина.
        """
        return reverse_lazy('user_profile', kwargs={'pk': self.request.user.pk})


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
