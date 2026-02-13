from django.urls import path
from rest_framework.permissions import AllowAny

from users.apps import UsersConfig
from users.views import PaymentsListApiView, CreateAPIView, SubscriptionApiView, \
    PaymentCreateApiView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = "users"

urlpatterns = [
    path("register/", CreateAPIView.as_view(), name="register"),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),

    path("subscription/", SubscriptionApiView.as_view(), name='subscription'),
    path("payments/", PaymentsListApiView.as_view(), name="payments-list"),
    path("payments/create/", PaymentCreateApiView.as_view(), name="payment-create"),
]
