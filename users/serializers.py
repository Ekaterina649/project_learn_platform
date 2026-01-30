from rest_framework import serializers

from users.models import Payments, User


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.setdefault('is_active', True)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

