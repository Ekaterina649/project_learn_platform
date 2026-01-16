from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None

    phone_number = models.CharField(max_length=11, blank=True, null=True, help_text='Укажите номер телефона')
    city = models.CharField(max_length=30, blank=True, null=True, help_text='Укажите город')
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True, help_text='Укажите аватар')
    email = models.EmailField(unique=True, verbose_name='Email')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'



