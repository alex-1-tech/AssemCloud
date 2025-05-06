from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db import models

# Валидатор для проверки корректности номера телефона
# Допускается формат с "+" и от 9 до 15 цифр
PHONE_VALIDATOR = RegexValidator(
    regex=r'^\+?\d{9,15}$',
    message=_("Номер телефона должен быть в формате: '+99999999999'. От 9 до 15 цифр.")
)

# Унифицированная функция для создания внешнего ключа на модель User
# Используется с заданным related_name и verbose_name
def user_fk(related_name, verbose_name):
    return models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name=related_name,
        verbose_name=verbose_name
    )

class TimeStampedModelWithUser(models.Model):
    """
    Абстрактная модель, добавляющая поля временных меток и пользователя,
    создавшего и обновившего объект.
    """
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))  # Дата создания
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))    # Дата последнего изменения
    created_by = user_fk("%(class)s_created", _("Создано пользователем"))            # Кто создал
    updated_by = user_fk("%(class)s_updated", _("Обновлено пользователем"))          # Кто обновил

    class Meta:
        abstract = True

class ReprMixin(models.Model):
    """
    Абстрактный миксин для реализации удобного строкового представления (__repr__).
    """
    class Meta:
        abstract = True

    def __repr__(self):
        # Возвращает строку вида: <ClassName id>
        return f"<{self.__class__.__name__} {self.pk}>"

# Универсальные функции нормализации (обработки) значений полей

def normalize_phone(value):
    # Удаляет пробелы и обрезает лишние пробелы по краям
    return value.replace(" ", "").strip() if value else value

def normalize_email(value):
    # Приводит email к нижнему регистру и удаляет пробелы
    return value.lower().strip() if value else value

def normalize_country(value):
    # Приводит код страны к верхнему регистру
    return value.upper()

def normalize_language(value):
    # Приводит код языка к нижнему регистру
    return value.lower()

def normalize_name(value):
    # Удаляет пробелы в начале и в конце строки
    return value.strip()

class NormalizeMixin(models.Model):
    """
    Абстрактный миксин, автоматически нормализующий значения полей при валидации.
    Ищет метод normalize_<field_name> и применяет его к соответствующему полю.
    """
    class Meta:
        abstract = True

    def clean(self):
        """
        Переопределяет метод clean(), чтобы выполнить нормализацию
        значений всех полей, для которых определены normalize_<fieldname> методы.
        """
        super().clean()

        for field in self._meta.fields:
            field_name = field.name
            normalize_method = getattr(self, f'normalize_{field_name}', None)  # Ищет метод normalize_<имя_поля>
            if callable(normalize_method):
                value = getattr(self, field_name)
                if value is not None:
                    setattr(self, field_name, normalize_method(value))  # Применяет нормализацию

    # Методы нормализации конкретных полей. Используются в clean()

    @staticmethod
    def normalize_email(value):
        return normalize_email(value)

    @staticmethod
    def normalize_phone(value):
        return normalize_phone(value)

    @staticmethod
    def normalize_country(value):
        return normalize_country(value)

    @staticmethod
    def normalize_language(value):
        return normalize_language(value)

    @staticmethod
    def normalize_name(value):
        return normalize_name(value)

    @staticmethod
    def normalize_version(value):
        return normalize_name(value)
