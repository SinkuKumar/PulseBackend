from rest_framework import serializers
from .models import LoginSession


class LoginSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginSession
        fields = ['jti', 'user_agent', 'ip_address', 'created_at', 'is_revoked']
