from django.urls import path

from users.views import PaymentsListApiView

app_name = 'users'



urlpatterns = [
    path("payments/", PaymentsListApiView.as_view()),
]

