from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import User



class MaterialTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )

        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123'
        )

        moderators_group, _ = Group.objects.get_or_create(name='Модератор')
        self.moderator.groups.add(moderators_group)

        self.course = Course.objects.create(
            title='testcourse',
            description='test course',
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            title='testlesson',
            owner=self.user,
            course=self.course,
            description='test lesson',
            video_link='https://www.youtube.com/watch?v=test123'
        )

        self.lessons_list_url = reverse('materials:lessons-list')
        self.lesson_detail_url = reverse('materials:lesson-detail', args=[self.lesson.id])
        self.lesson_create_url = reverse('materials:lesson-create')
        self.lesson_update_url = reverse('materials:lesson-update', args=[self.lesson.id])
        self.lesson_delete_url = reverse('materials:lesson-delete', args=[self.lesson.id])

        # Для курсов :
        self.courses_list_url = reverse('materials:courses-list')
        self.course_detail_url = reverse('materials:courses-detail', args=[self.course.id])

    def test_user_can_view_own_lesson(self):
        """Обычный пользователь может просматривать свой урок"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'testlesson')

    def test_user_can_create_lesson(self):
        """Обычный пользователь может создавать уроки"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Новый урок',
            'description': 'Описание нового урока',
            'course': self.course.id,
            'video_link': 'https://www.youtube.com/watch?v=new123'
        }
        response = self.client.post(self.lesson_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(response.data['owner'], self.user.id)

    def test_user_can_update_own_lesson(self):
        """Обычный пользователь может обновлять свой урок"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Обновленный урок'}
        response = self.client.patch(self.lesson_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Обновленный урок')

    def test_user_can_delete_own_lesson(self):
        """Обычный пользователь может удалять свой урок"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_user_cannot_create_lesson_without_youtube_link(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Новый урок',
            'description': 'Описание',
            'course': self.course.id,
            'video_link': 'https://vimeo.com/123'
        }
        response = self.client.post(self.lesson_create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

        # Получаем текст ошибки из списка
        error_messages = response.data['non_field_errors']
        error_text = str(error_messages[0])

        # Проверяем конкретное сообщение
        self.assertEqual(error_text, 'Недопустимый формат ссылки')

    def test_moderator_can_view_all_lessons(self):
        """Модератор может видеть все уроки"""
        other_user = User.objects.create_user(email='other@test.com')
        Lesson.objects.create(
            title='Чужой урок',
            description='...',
            course=self.course,
            owner=other_user
        )

        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_moderator_can_update_any_lesson(self):
        """Модератор может обновлять любой урок"""
        self.client.force_authenticate(user=self.moderator)
        data = {'title': 'От модератора',}
        response = self.client.patch(self.lesson_update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'От модератора')

    def test_moderator_cannot_create_lesson(self):
        """Модератор НЕ может создавать уроки"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'title': 'Новый урок от модератора',
            'description': '...',
            'course': self.course.id,
            'video_link': 'https://www.youtube.com/watch?v=moderator'
        }
        response = self.client.post(self.lesson_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_cannot_delete_lesson(self):
        """Модератор НЕ может удалять уроки"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(self.lesson_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_anonymous_cannot_view_lessons(self):
        """Неавторизованный пользователь не может видеть уроки"""
        response = self.client.get(self.lessons_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_cannot_create_lesson(self):
        """Неавторизованный пользователь не может создавать уроки"""
        data = {'title': 'Новый урок'}
        response = self.client.post(self.lesson_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_creation_requires_course(self):
        """При создании урока обязательно указывать курс"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Урок без курса',
            'video_link': 'https://www.youtube.com/watch?v=test'
        }
        response = self.client.post(self.lesson_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('course', response.data)