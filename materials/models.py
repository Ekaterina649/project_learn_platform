from django.conf import settings
from django.db import models

from users.models import User


class Course(models.Model):

    title = models.CharField(
        max_length=20, help_text="Укажите навзание курса", verbose_name="Название"
    )
    preview = models.ImageField(
        upload_to="course_preview/",
        blank=True,
        null=True,
        help_text="Загрузите картинку для курса",
        verbose_name="Превью",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Укажите описание для курса",
        verbose_name="Описание",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        blank=True,
        null=True,
        help_text="Укажите владельца",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):

    title = models.CharField(
        max_length=20, help_text="Укажите навзание урока", verbose_name="Название"
    )
    preview = models.ImageField(
        upload_to="course_preview/",
        blank=True,
        null=True,
        help_text="Загрузите картинку для урока",
        verbose_name="Превью",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Укажите описание для курса",
        verbose_name="Описание",
    )
    video_link = models.URLField(
        verbose_name="Ссылка на видео",
        blank=True,
        null=True,
        help_text="Укажите ссылку на видео урока",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
        help_text="Выберите курс",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        blank=True,
        null=True,
        help_text="Укажите владельца",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
