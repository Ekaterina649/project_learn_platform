from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import User, Subscription


class SubscriptionTestCase(APITestCase):

    def setUp(self):

        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123'
        )

        # Добавляем модератора в группу
        moderators_group, _ = Group.objects.get_or_create(name='Модератор')
        self.moderator.groups.add(moderators_group)

        self.course1 = Course.objects.create(
            title='Курс 1',
            description='Описание курса 1',
            owner=self.user1
        )
        self.course2 = Course.objects.create(
            title='Курс 2',
            description='Описание курса 2',
            owner=self.user2
        )

        self.subscription_url = reverse('users:subscription')

        self.course_list_url = reverse('materials:courses-list')
        self.course_detail_url = reverse('materials:courses-detail', args=[self.course1.id])


    def test_user_can_subscribe_to_course(self):
        """Пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.user1)

        data = {'course_id': self.course2.id}
        response = self.client.post(self.subscription_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['is_subscribed'])
        self.assertTrue(Subscription.objects.filter(
            user=self.user1,
            course=self.course2
        ).exists())

    def test_user_can_unsubscribe_from_course(self):
        """Пользователь может отписаться от курса"""
        # Сначала подписываемся
        Subscription.objects.create(user=self.user1, course=self.course2)

        # Затем отписываемся
        self.client.force_authenticate(user=self.user1)
        data = {'course_id': self.course2.id}
        response = self.client.post(self.subscription_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['is_subscribed'])
        self.assertFalse(Subscription.objects.filter(
            user=self.user1,
            course=self.course2
        ).exists())
