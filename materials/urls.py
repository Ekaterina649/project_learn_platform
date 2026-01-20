from django.urls import path, include
from rest_framework import routers


from materials.views import (
    CourseViewSet,
    LessonListApiView,
    LessonRetrieveApiView,
    LessonCreateApiView,
    LessonUpdateApiView,
    LessonDestroyApiView,
)

app_name = "materials"


router = routers.DefaultRouter()
router.register("courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("", include(router.urls)),
    path("lessons/", LessonListApiView.as_view()),
    path("lessons/<int:pk>/", LessonRetrieveApiView.as_view()),
    path("lessons/create/", LessonCreateApiView.as_view()),
    path("lessons/update/<int:pk>/", LessonUpdateApiView.as_view()),
    path("lessons/delete/<int:pk>/", LessonDestroyApiView.as_view()),
]
