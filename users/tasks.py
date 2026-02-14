from django.utils import timezone
from datetime import timedelta

from celery import shared_task

from users.models import User


@shared_task
def checking_user_activity():

    one_month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)

    for user in inactive_users:
        user.is_active = False
        user.save()