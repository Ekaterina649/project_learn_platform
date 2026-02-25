from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django.db import models

from materials.models import Course, Lesson
from materials.pagination import PaginationMaterials
from materials.serializers import CourseSerializer, LessonSerializer
from users.models import Subscription
from materials.tasks import send_email
from users.permissions import IsModer, IsOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class  = PaginationMaterials

    def perform_create(self, serializer):
        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (~IsModer,)
        elif self.action in ["update","retrieve"]:
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == 'destroy':
            self.permission_classes = (~IsModer | IsOwner,)
        return [perm() for perm in self.permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name='Модератор').exists():
            return qs
        return qs.filter(
            models.Q(owner=user) |
            models.Q(subscriptions__user=user)  # Используем related_name
        ).distinct()

    def perform_update(self, serializer):
        course = serializer.save()

        emails = Subscription.objects.filter(course=course) \
            .values_list('user__email', flat=True)

        for email in emails:
            send_email.delay(email, course.title)





class LessonListApiView(generics.ListAPIView):
    queryset = Lesson.objects.all().order_by('id')
    serializer_class = LessonSerializer
    pagination_class = PaginationMaterials

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.groups.filter(name='Модератор').exists():
            qs = qs.filter(owner=self.request.user)
        return qs



class LessonCreateApiView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()

        course = lesson.course

        emails = Subscription.objects.filter(course=course) \
            .values_list('user__email', flat=True)

        for email in emails:
            send_email.delay(email, course.title)

    permission_classes = [IsAuthenticated,~IsModer]


class LessonRetrieveApiView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonUpdateApiView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]

class LessonDestroyApiView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner | ~IsModer]
