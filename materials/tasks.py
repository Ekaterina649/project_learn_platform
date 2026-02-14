from celery import shared_task
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER


@shared_task
def send_email(email, course):
    send_mail('Обновление', f'Курс «{course}» обновлен! Посмотрите, что там нового.',
              EMAIL_HOST_USER, [email])