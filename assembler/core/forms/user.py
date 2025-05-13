from django import forms
from core.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.password_validation import validate_password

class UserRegistrationForm(forms.ModelForm):
    """
    Форма для регистрации нового пользователя. Включает:
    - email (уникальный логин)
    - имя и фамилию
    - телефон и адрес (опционально)
    - пароль + подтверждение пароля
    """

    # Основной пароль
    password1 = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput,
    )

    # Подтверждение пароля
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "address")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'example@mail.com',
            'phone': '+79991234567',
            'address': 'Ваш адрес',
            'password1': 'Введите пароль',
            'password2': 'Повторите пароль',
        }
        for name, text in placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs['placeholder'] = text

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })

    def clean_email(self):
        """
        Проверка на уникальность email. Если пользователь с таким email уже есть — ошибка.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Пользователь с таким email уже существует."))
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password(password)
        return password

    def clean(self):
        """
        Проверка совпадения паролей.
        Если введены оба пароля, но они не совпадают — добавляется ошибка в поле password2.
        """
        cleaned_data = super().clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error("password2", _("Пароли не совпадают."))
        return cleaned_data

    def save(self, commit=True):
        """
        Переопределение метода сохранения:
        - Устанавливает хэшированный пароль на основе password1
        - Сохраняет пользователя в БД, если `commit=True`
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    """
    Форма авторизации пользователя по email и паролю.
    Выполняет проверку учетных данных через `authenticate`.
    """

    email = forms.EmailField(
        label=_("email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com',
        })
    )

    password = forms.CharField(
        label=_("password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        })
    )

    def clean(self):
        """
        Переопределение метода clean для валидации логина.
        Проверяет корректность введенных email и пароля.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError(_("Неверный email или пароль"))
            
            if not getattr(user, 'is_email_verified', False):
                raise forms.ValidationError(_("Email не подтверждён. Проверьте почту."))
            
            self.user = user
        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    """
    Форма для обновления профиля пользователя.
    Позволяет редактировать имя, фамилию, email, телефон и адрес.
    """
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "address")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'example@mail.com',
            'phone': '+79991234567',
            'address': 'Ваш адрес',
        }
        for name, text in placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs['placeholder'] = text

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })

    def clean_email(self):
        """
        Проверка уникальности email при изменении.
        Исключает текущего пользователя из проверки.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("Пользователь с таким email уже существует."))
        return email

class UserPasswordChangeForm(PasswordChangeForm):
    """
    Форма смены пароля авторизованного пользователя.
    Наследуется от стандартной PasswordChangeForm и добавляет стили и placeholder'ы.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = {
            'old_password': 'Старый пароль',
            'new_password1': 'Новый пароль',
            'new_password2': 'Подтверждение нового пароля',
        }

        placeholders = {
            'old_password': 'Введите текущий пароль',
            'new_password1': 'Новый пароль',
            'new_password2': 'Подтвердите новый пароль',
        }

        for name, placeholder in placeholders.items():
            self.fields[name].label = labels.get(name, self.fields[name].label)
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': placeholder
            })

class UserSetPasswordForm(SetPasswordForm):
    """
    Форма для установки нового пароля после сброса.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        labels = {
            'new_password1': 'Новый пароль',
            'new_password2': 'Подтверждение нового пароля',
        }

        placeholders = {
            'new_password1': 'Введите новый пароль',
            'new_password2': 'Повторите новый пароль',
        }

        for name, placeholder in placeholders.items():
            self.fields[name].label = labels.get(name)
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': placeholder
            })
