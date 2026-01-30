import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, filters

from users.models import Payments
from users.serializers import PaymentsSerializer


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
    filterset_fields = ['course', 'lesson','payment_method']
    ordering_fields = ['payment_date', 'amount', 'id']
    search_fields = ['-payment_date']