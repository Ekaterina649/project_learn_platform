from django.core.management.base import BaseCommand

from users.constants import PAYMENT_METHOD_CASH, PAYMENT_METHOD_TRANSFER
from users.models import Payments, User
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создание тестовых платежей'

    TEST_COURSE_AMOUNT = 500
    TEST_LESSON_AMOUNT = 1500

    def handle(self, *args, **kwargs):
        user = User.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not user or not (course or lesson):
            self.stdout.write(
                self.style.ERROR('Нет пользователей, курсов или уроков')
            )
            return

        Payments.objects.create(
            user = user,
            course=course,
            amount=self.TEST_COURSE_AMOUNT,
            payment_method=PAYMENT_METHOD_CASH,
        )

        Payments.objects.create(
            user = user,
            lesson=lesson,
            amount=self.TEST_LESSON_AMOUNT,
            payment_method=PAYMENT_METHOD_TRANSFER,
        )

        self.stdout.write(
            self.style.SUCCESS('Платежи успешно созданы')
        )


