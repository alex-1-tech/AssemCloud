from django.urls import reverse
from django.utils import timezone
from core.models.base import _, models, NormalizeMixin, PHONE_VALIDATOR, normalize_email, ReprMixin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    """
    Менеджер для создания пользователей и суперпользователей.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email обязателен'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создание суперпользователя с обязательными правами.
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
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.CharField(max_length=20,blank=True,validators=[PHONE_VALIDATOR])

    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.email:
            self.email = normalize_email(self.email)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("user_detail", kwargs={"pk": self.pk})

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name or self.email or ""

    class Meta:
        db_table = 'users'
