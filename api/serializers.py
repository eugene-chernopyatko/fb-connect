from rest_framework import serializers
from authentication.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'project_count', 'billing_plan']