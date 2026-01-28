from rest_framework import serializers
from .models import Project, Task
from organization.models import Employee
from organization.serializers import EmployeeSerializer


class ProjectSerializer(serializers.ModelSerializer):
    history = serializers.HyperlinkedIdentityField(
        view_name="project-history-list",
        lookup_field="pk",
        lookup_url_kwarg="project_pk",
    )

    created_by = serializers.HyperlinkedRelatedField(
        view_name="employee-detail", read_only=True
    )
    members = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="employee-detail"
    )

    member_ids = serializers.PrimaryKeyRelatedField(
        source="members",
        many=True,
        queryset=Employee.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            "url",
            "name",
            "description",
            "planned_start",
            "planned_end",
            "actual_start",
            "actual_end",
            "created_at",
            "created_by",
            "members",
            "member_ids",
            "history",
        ]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class ProjectHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.StringRelatedField(read_only=True)
    history_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Project.history.model
        fields = "__all__"

    def get_changed_by(self, obj):
        return obj.history_user.username if obj.history_user else None


class TaskSerializer(serializers.ModelSerializer):
    created_by = EmployeeSerializer(read_only=True)
    assigned_by = EmployeeSerializer(read_only=True)
    assigned_to = EmployeeSerializer(many=True, read_only=True)

    # Write-only relation fields
    created_by_id = serializers.PrimaryKeyRelatedField(
        source="created_by",
        queryset=Employee.objects.all(),
        write_only=True,
        required=False,
    )
    assigned_by_id = serializers.PrimaryKeyRelatedField(
        source="assigned_by",
        queryset=Employee.objects.all(),
        write_only=True,
        required=False,
    )
    assigned_to_ids = serializers.PrimaryKeyRelatedField(
        source="assigned_to",
        many=True,
        queryset=Employee.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "title",
            "description",
            "planned_start",
            "planned_end",
            "actual_start",
            "actual_end",
            "status",
            "created_at",
            "created_by",
            "created_by_id",
            "assigned_by",
            "assigned_by_id",
            "assigned_to",
            "assigned_to_ids",
        ]
