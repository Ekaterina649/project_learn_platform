from rest_framework import serializers
from materials.models import Course
from users.constants import PAYMENT_METHODS, PAYMENT_METHOD_TRANSFER
from users.models import Payments, User, Subscription


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания платежа за КУРС (POST)"""
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        required=True
    )

    payment_method = serializers.ChoiceField(
        choices=[choice[0] for choice in PAYMENT_METHODS],
        default=PAYMENT_METHOD_TRANSFER
    )

    class Meta:
        model = Payments
        fields = ("course", "amount", "payment_method")
        extra_kwargs = {
            'amount': {'required': True},
        }

    def validate(self, data):
        """Проверяем сумму"""
        if data.get('amount') and data['amount'] <= 0:
            raise serializers.ValidationError(
                "Сумма оплаты должна быть больше 0"
            )
        return data


class PaymentListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения платежей (GET)"""
    course_title = serializers.CharField(source='course.title', read_only=True, allow_null=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True, allow_null=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Payments
        fields = (
            "id", "user_email", "payment_date", "course", "course_title",
             "amount", "payment_method",
            "payment_url", "stripe_session_id"
        )
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        validated_data.setdefault("is_active", True)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
        read_only_fields = ['user',]