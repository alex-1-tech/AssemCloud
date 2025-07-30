"""Models for Machine and Converter entities in the system."""

from typing import ClassVar

from django.db import models


class Machine(models.Model):
    """Represent a machine entity."""

    # Основная информация
    serial_number = models.CharField("Серийный номер", max_length=100, unique=True)

    # ПО
    SOFTWARE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("Кальмар", "Кальмар"),
        ("Фазар", "Фазар"),
    ]
    software = models.CharField("ПО", max_length=100, choices=SOFTWARE_CHOICES)
    software_version = models.CharField("Версия ПО", max_length=50)

    # Зарядка планшета
    tablet_charger_voltage = models.CharField(
        "Зарядка планшета (напряжение)",
        max_length=50,
        default="15V",
    )

    # Зарядное устройство
    CHARGER_MODEL_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("1", "Модель 1"),
        ("2", "Модель 2"),
        ("3", "Модель 3"),
    ]
    charger_model = models.CharField(
        "Модель зарядного устройства",
        max_length=50,
        choices=CHARGER_MODEL_CHOICES,
    )
    charger_voltage = models.CharField(
        "Напряжение зарядного устройства",
        max_length=50,
        default="16.8V",
    )
    charger_current = models.CharField(
        "Ток зарядного устройства",
        max_length=50,
        default="5A",
    )

    # Адаптер питания
    POWER_ADAPTER_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("15V 4.5A 100-240V (Dopler)", "15V 4.5A 100-240V (Dopler)"),
        ("12V 5A 100-240V (AOS)", "12V 5A 100-240V (AOS)"),
    ]
    power_adapter = models.CharField(
        "Адаптер питания",
        max_length=100,
        choices=POWER_ADAPTER_CHOICES,
    )

    # Аккумулятор
    BATTERY_VOLTAGE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("15V (Dopler)", "15V (Dopler)"),
        ("12V (AOS)", "12V (AOS)"),
    ]
    battery_voltage = models.CharField(
        "Напряжение батареи",
        max_length=50,
        choices=BATTERY_VOLTAGE_CHOICES,
    )
    battery_capacity = models.CharField(
        "Ёмкость батареи",
        max_length=50,
        default="24А/ч",
    )
    battery_serial = models.CharField("Серийный номер батареи", max_length=100)

    # УЗК
    UZK_TYPE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("16/64 (кальмар)", "16/64 (кальмар)"),
        ("16/128 (фазар)", "16/128 (фазар)"),
    ]
    uzk_type = models.CharField("Тип УЗК", max_length=50, choices=UZK_TYPE_CHOICES)
    uzk_serial = models.CharField("Серийный номер УЗК", max_length=100)

    UZK_MANUFACTURER_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("AOS (Франция)", "AOS (Франция)"),
        ("Dopler (Китай)", "Dopler (Китай)"),
    ]
    uzk_manufacturer = models.CharField(
        "Производитель УЗК",
        max_length=100,
        choices=UZK_MANUFACTURER_CHOICES,
    )

    # Драйверы
    DRIVER_TYPE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("AOS", "AOS"),
        ("Dopler", "Dopler"),
    ]
    driver_type = models.CharField(
        "Тип драйвера",
        max_length=100,
        choices=DRIVER_TYPE_CHOICES,
    )
    driver_serial = models.CharField("Серийный номер драйвера", max_length=100)
    soc_serial = models.CharField("Серийный номер SOC", max_length=100)

    # Кабель
    CABLE_TIP_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("RJ45/RJ45", "RJ45/RJ45"),
        ("RJ45/RJ45 (защищенный)", "RJ45/RJ45 (защищенный)"),
    ]
    cable_tip = models.CharField(
        "Тип наконечника кабеля",
        max_length=50,
        choices=CABLE_TIP_CHOICES,
    )

    # Шасси
    CHASSIS_TYPE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("стойка", "Стойка"),
        ("тележка", "Тележка"),
    ]
    chassis_type = models.CharField(
        "Тип рамы шасси",
        max_length=50,
        choices=CHASSIS_TYPE_CHOICES,
    )

    # РСП
    RSP_VERSION_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("1", "Версия 1"),
        ("2", "Версия 2"),
        ("3", "Версия 3"),
        ("4", "Версия 4"),
    ]
    rsp_version = models.CharField(
        "Версия исполнения РСП",
        max_length=20,
        choices=RSP_VERSION_CHOICES,
    )

    # Сканер
    SCANNER_TYPE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("Р50", "Р50"),
        ("Р65", "Р65"),
        ("UIC60", "UIC60"),
        ("IRS52", "IRS52"),
    ]
    scanner_type = models.CharField(
        "Тип сканера",
        max_length=50,
        choices=SCANNER_TYPE_CHOICES,
    )

    SCANNER_VERSION_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("Стационарный (РСП)", "Стационарный (РСП)"),
        ("Путевой", "Путевой"),
    ]
    scanner_version = models.CharField(
        "Версия сканера",
        max_length=50,
        choices=SCANNER_VERSION_CHOICES,
    )

    # Планшет
    tablet_brand = models.CharField("Фирма планшета", max_length=50)
    tablet_model = models.CharField("Модель планшета", max_length=100)
    tablet_serial = models.CharField("Серийный номер планшета", max_length=100)
    tablet_os = models.CharField("ОС планшета", max_length=50)
    tablet_driver1 = models.CharField("DRIVER1", max_length=100)
    tablet_driver1_version = models.CharField("Версия DRIVER1", max_length=50)
    tablet_driver2 = models.CharField("DRIVER2", max_length=100)
    tablet_driver2_version = models.CharField("Версия DRIVER2", max_length=50)

    # Даты
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата изменения", auto_now=True)

    class Meta:
        """Meta options for Machine."""

        verbose_name = "Машина"
        verbose_name_plural = "Машины"
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of the machine."""
        return f"{self.serial_number} — {self.software} v{self.software_version}"


class Converter(models.Model):
    """Represent a converter associated with a machine."""

    TYPE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("наклонный", "Наклонный"),
        ("прямой", "Прямой"),
        ("ручной", "Ручной"),
    ]
    CONNECTOR_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("RJ45/RJ45", "RJ45/RJ45"),
        ("RJ45/RJ45(защищённый)", "RJ45/RJ45 (защищённый)"),
    ]

    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="converters",
        verbose_name="Машина",
    )
    type = models.CharField("Тип преобразователя", max_length=50, choices=TYPE_CHOICES)
    serial = models.CharField("Серийный номер преобразователя", max_length=100)
    frequency = models.CharField("Рабочая частота", max_length=50)
    release_date = models.DateField("Дата выпуска", null=True, blank=True)
    connector_type = models.CharField(
        "Тип разъёма",
        max_length=50,
        choices=CONNECTOR_CHOICES,
    )

    class Meta:
        """Meta options for Converter."""

        verbose_name = "Преобразователь"
        verbose_name_plural = "Преобразователи"

    def __str__(self) -> str:
        """Return string representation of the converter."""
        return f"{self.get_type_display()} ({self.serial})"
