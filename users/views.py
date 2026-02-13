from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course
from users.models import Payments, User, Subscription
from users.serializers import (
    UserSerializer,
    PaymentCreateSerializer,
    PaymentListSerializer,
)
from users.services.stripe import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_session,
)


class UserViewSet(viewsets.ViewSet):
    """Временный ViewSet для исправления миграций"""
    pass


class PaymentsListApiView(generics.ListAPIView):
    queryset = Payments.objects.all()
    serializer_class = PaymentListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date", "amount", "id"]
    search_fields = ["-payment_date"]

    def get_queryset(self):
        """Показываем только платежи текущего пользователя"""
        return Payments.objects.filter(user=self.request.user)


class PaymentCreateApiView(generics.CreateAPIView):
    """
    POST /users/payments/create/
    Создание платежа за КУРС и получение ссылки на оплату Stripe
    """
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = self.perform_create(serializer)

            # Возвращаем полный ответ с данными о Stripe
            response_data = {
                "id": payment.id,
                "course": payment.course.id,
                "course_title": payment.course.title,
                "amount": str(payment.amount),
                "payment_method": payment.payment_method,
                "payment_url": payment.payment_url,
                "stripe_session_id": payment.stripe_session_id,
                "message": "Платеж создан успешно. Используйте payment_url для оплаты."
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Ошибка при создании платежа: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        user = self.request.user

        # Сохраняем базовые данные платежа
        payment = serializer.save(user=user)

        # Создаем продукт в Stripe для курса
        product_name = f"Курс: {payment.course.title}"
        product_description = payment.course.description[:500] if payment.course.description else ""

        try:
            # Создаем продукт в Stripe
            stripe_product = create_stripe_product(
                name=product_name,
                description=product_description
            )

            # Создаем цену в Stripe
            stripe_price = create_stripe_price(
                product_id=stripe_product.id,
                amount=float(payment.amount)
            )

            # Создаем сессию оплаты в Stripe
            success_url = "http://127.0.0.1:8000/success/"
            cancel_url = "http://127.0.0.1:8000/cancel/"

            stripe_session = create_stripe_session(
                price_id=stripe_price.id,
                success_url=success_url,
                cancel_url=cancel_url
            )

            # Сохраняем данные Stripe в наш платеж
            payment.stripe_product_id = stripe_product.id
            payment.stripe_price_id = stripe_price.id
            payment.stripe_session_id = stripe_session.id
            payment.payment_url = stripe_session.url
            payment.save()

            return payment

        except Exception as e:
            payment.delete()
            raise ValidationError(f"Ошибка при создании платежа в Stripe: {str(e)}")


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