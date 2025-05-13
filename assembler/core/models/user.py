from django.urls import reverse
from django.utils import timezone
from core.models.base import _, models, NormalizeMixin, PHONE_VALIDATOR, normalize_email, ReprMixin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    """
    Менеджер для создания пользователей и суперпользователей.

    Этот класс управляет созданием пользователей и суперпользователей. Он переопределяет
    стандартные методы для создания пользователя и суперпользователя с использованием
    кастомных полей модели пользователя (например, email в качестве уникального идентификатора).
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создание обычного пользователя.

        :param email: Электронная почта пользователя (обязательное поле).
        :param password: Пароль пользователя (опционально).
        :param extra_fields: Дополнительные поля пользователя.
        :return: Созданный пользователь.
        """
        if not email:
            raise ValueError(_('Email обязателен'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)  # Создание пользователя.
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создание суперпользователя с обязательными правами.

        :param email: Электронная почта суперпользователя (обязательное поле).
        :param password: Пароль суперпользователя (опционально).
        :param extra_fields: Дополнительные поля для суперпользователя.
        :return: Созданный суперпользователь.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser должен иметь is_staff=True."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser должен иметь is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(ReprMixin, NormalizeMixin, AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя с расширениями.

    Модель пользователя, которая расширяет стандартную модель Django `AbstractBaseUser` 
    для использования email в качестве уникального идентификатора и добавляет 
    дополнительные поля, такие как имя, фамилия, телефон, адрес и статус.
    Также включает методы для работы с именами и сохранением.
    """

    # Имя пользователя (обязательное поле).
    first_name = models.CharField(_("Имя"), max_length=100)
    
    # Фамилия пользователя (обязательное поле).
    last_name = models.CharField(_("Фамилия"), max_length=100)
    
    # Электронная почта пользователя (уникальное поле).
    email = models.EmailField(_("Почта"), unique=True, blank=False, null=False)
    
    # Телефон пользователя (необязательное поле с валидацией).
    phone = models.CharField(_("Телефон"), max_length=20, blank=True, validators=[PHONE_VALIDATOR])

    # Адрес пользователя (необязательное поле).
    address = models.TextField(_("Адрес"), blank=True)
    
    # Флаг активности пользователя (по умолчанию True).
    is_active = models.BooleanField(_("Активен"), default=True)
    
    # Флаг того, является ли пользователь сотрудником (по умолчанию False).
    is_staff = models.BooleanField(_("Сотрудник"), default=False)
    
    # Дата регистрации пользователя (по умолчанию текущая дата и время).
    date_joined = models.DateTimeField(_("Дата регистрации"), default=timezone.now)

    # Подтверждение почты пользователя
    is_email_verified = models.BooleanField(default=False)

    # Менеджер для работы с пользователями.
    objects = UserManager()

    # Поле для использования в качестве уникального идентификатора пользователя.
    USERNAME_FIELD = 'email'
    
    # Дополнительные обязательные поля, помимо USERNAME_FIELD.
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        """
        Переопределение метода сохранения для нормализации email перед сохранением.
        """
        if self.email:
            self.email = normalize_email(self.email)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL для страницы профиля пользователя.
        """
        return reverse("user_detail", kwargs={"pk": self.pk})

    def get_full_name(self):
        """
        Возвращает полное имя пользователя (имя и фамилия).
        """
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """
        Возвращает сокращенное имя пользователя (либо имя, либо email, если имя отсутствует).
        """
        return self.first_name or self.email or ""

    class Meta:
        db_table = 'users'
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
