from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Employee, Designation, Level


class DesignationSerializer(serializers.ModelSerializer):
    history = serializers.HyperlinkedIdentityField(
        view_name="designation-history-list",
        lookup_field="pk",
        lookup_url_kwarg="designation_pk",
    )

    class Meta:
        model = Designation
        fields = [
            "url",
            "title",
            "level",
            "description",
            "created_on",
            "created_by",
            "history",
        ]
        read_only_fields = ("created_by",)

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class DesignationHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.StringRelatedField(read_only=True)
    history_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Designation.history.model
        fields = [
            "history_user",
            "history_date",
            "title",
            "level",
            "description",
            "history_type",
        ]

    def get_changed_by(self, obj):
        return obj.history_user.username if obj.history_user else None


class LevelSerializer(serializers.ModelSerializer):
    history = serializers.HyperlinkedIdentityField(
        view_name="level-history-list",
        lookup_field="pk",
        lookup_url_kwarg="level_pk",
    )

    class Meta:
        model = Level
        fields = [
            "url",
            "level",
            "description",
            "created_on",
            "created_by",
            "history",
        ]
        read_only_fields = ("created_on", "created_by")

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class LevelHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.StringRelatedField(read_only=True)
    history_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Level.history.model
        fields = [
            "history_user",
            "history_date",
            "level",
            "description",
            "history_type",
        ]

    def get_changed_by(self, obj):
        return obj.history_user.username if obj.history_user else None


class EmployeeSerializer(serializers.ModelSerializer):
    history = serializers.HyperlinkedIdentityField(
        view_name="employee-history-list",
        lookup_field="pk",
        lookup_url_kwarg="employee_pk",
    )

    user = UserSerializer()

    designation_id = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        source="designation",
        required=False,
        allow_null=True,
    )

    level_id = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        source="level",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Employee
        fields = (
            "url",
            "user",
            "designation_id",
            "level_id",
            "supervisor",
            "history",
        )

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:  # update case
            fields["user"].read_only = True
        return fields

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(**user_data)
        return Employee.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("user", None)  # ignore user on update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EmployeeHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.StringRelatedField(read_only=True)
    history_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Employee.history.model
        fields = "__all__"

    def get_changed_by(self, obj):
        return obj.history_user.username if obj.history_user else None
