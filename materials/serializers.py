from rest_framework import serializers

from materials.models import Course, Lesson
from materials.validators import VideoLinkValidator
from users.models import Subscription


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [VideoLinkValidator(field='video_link')]


class CourseSerializer(serializers.ModelSerializer):
    count_lessons = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_count_lessons(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяем, подписан ли текущий пользователь на этот курс"""
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False

        return Subscription.objects.filter(
            user=user,
            course=obj
        ).exists()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "count_lessons",
            "lessons",
            "is_subscribed"
        ]

