from rest_framework import serializers
from django.db import transaction
from .models import Employee
from django.contrib.auth.models import User
from users.serializers import UserSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = ('id', 'user', 'supervisor')

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')

        user = User.objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            email=user_data.get('email', '')
        )

        employee = Employee.objects.create(
            user=user,
            **validated_data
        )

        return employee

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr == 'password':
                    user.set_password(value)
                else:
                    setattr(user, attr, value)
            user.save()

        instance.supervisor = validated_data.get('supervisor', instance.supervisor)
        instance.save()

        return instance
