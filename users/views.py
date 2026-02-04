import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, filters, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course
from users.models import Payments, User, Subscription
from users.serializers import PaymentsSerializer, UserSerializer


class UserViewSet(viewsets.ViewSet):
    """Временный ViewSet для исправления миграций"""

    pass


class PaymentsListApiView(generics.ListAPIView):
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date", "amount", "id"]
    search_fields = ["-payment_date"]


class CreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)


class SubscriptionApiView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course_item = get_object_or_404(Course, id=course_id)

        # Проверяем, есть ли уже подписка
        subscription = Subscription.objects.filter(
            user=user,
            course=course_item
        )

        if subscription.exists():
            # Если подписка есть - удаляем ее
            subscription.delete()
            message = 'Подписка удалена'
            is_subscribed = False
        else:
            # Если подписки нет - создаем ее
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'
            is_subscribed = True

        return Response({
            "message": message,
            "is_subscribed": is_subscribed,
            "course_id": course_id,
            "course_title": course_item.title
        }, status=status.HTTP_200_OK)