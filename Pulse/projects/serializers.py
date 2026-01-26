from rest_framework import serializers
from .models import Project, Task
from organization.models import Employee
from organization.serializers import EmployeeSerializer


class ProjectSerializer(serializers.ModelSerializer):
    created_by = EmployeeSerializer(read_only=True)
    members = EmployeeSerializer(many=True, read_only=True)

    # Write-only fields for relations
    created_by_id = serializers.PrimaryKeyRelatedField(
        source="created_by",
        queryset=Employee.objects.all(),
        write_only=True,
        required=False,
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
            "id",
            "name",
            "description",
            "planned_start",
            "planned_end",
            "actual_start",
            "actual_end",
            "created_at",
            "created_by",
            "created_by_id",
            "members",
            "member_ids",
        ]


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
            "planned_time",
            "actual_time",
            "status",
            "created_at",
            "created_by",
            "created_by_id",
            "assigned_by",
            "assigned_by_id",
            "assigned_to",
            "assigned_to_ids",
        ]
