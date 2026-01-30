from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


from users.constants import PAYMENT_METHODS


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    phone_number = models.CharField(
        max_length=11, blank=True, null=True, help_text="Укажите номер телефона"
    )
    city = models.CharField(
        max_length=30, blank=True, null=True, help_text="Укажите город"
    )
    avatar = models.ImageField(
        upload_to="avatar/", blank=True, null=True, help_text="Укажите аватар"
    )
    email = models.EmailField(unique=True, verbose_name="Email")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payments(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оплаты",
    )
    course = models.ForeignKey(
        'materials.Course',
        on_delete=models.CASCADE,
        related_name="payments",
        blank=True,
        null=True,
        verbose_name="Оплаченный курс",
    )
    lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.CASCADE,
        related_name="payments",
        blank=True,
        null=True,
        verbose_name="Оплаченный урок",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name="Способ оплаты",
        help_text="Выберите способ оплаты",
    )

    def __str__(self):
        if self.course:
            return f"{self.user.email} - {self.course.title} - {self.amount}"
        elif self.lesson:
            return f"{self.user.email} - {self.lesson.title} - {self.amount}"
        return f"{self.user.email} - {self.amount}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
