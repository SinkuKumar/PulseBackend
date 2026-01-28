from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Employee, Designation, Level


class DesignationSerializer(serializers.ModelSerializer):
    history = serializers.HyperlinkedIdentityField(
        view_name="designation-history-list",
        lookup_field="pk",
        lookup_url_kwarg="designation_pk",
    )

    created_by = serializers.HyperlinkedRelatedField(
        view_name="employee-detail", read_only=True
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
    
    created_by = serializers.HyperlinkedRelatedField(
        view_name="employee-detail", read_only=True
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

    # READ (representation)
    user = serializers.HyperlinkedRelatedField(
        view_name="user-detail",
        read_only=True,
    )

    designation = serializers.HyperlinkedRelatedField(
        view_name="designation-detail",
        read_only=True,
    )

    level = serializers.HyperlinkedRelatedField(
        view_name="level-detail",
        read_only=True,
    )

    supervisor = serializers.HyperlinkedRelatedField(
        view_name="employee-detail",
        read_only=True,
    )

    # WRITE (input only)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
        required=False,
        allow_null=True,
    )

    designation_id = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        source="designation",
        write_only=True,
        required=False,
        allow_null=True,
    )

    level_id = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        source="level",
        write_only=True,
        required=False,
        allow_null=True,
    )

    supervisor_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source="employee",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Employee
        fields = (
            "url",
            "employee_id",
            "user",
            "user_id",
            "designation",
            "designation_id",
            "level",
            "level_id",
            "supervisor",
            "supervisor_id",
            "history",
        )


class EmployeeHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.StringRelatedField(read_only=True)
    history_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Employee.history.model
        fields = "__all__"

    def get_changed_by(self, obj):
        return obj.history_user.username if obj.history_user else None
