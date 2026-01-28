from rest_framework import serializers
from .models import Project, Task, Comment
from organization.models import Employee


class CommentSerializer(serializers.ModelSerializer):
    task = serializers.HyperlinkedRelatedField(
        view_name="task-detail",
        read_only=True,
    )
    created_by = serializers.HyperlinkedRelatedField(
        view_name="employee-detail",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "task",
            "created_by",
            "comment",
            "created_at",
        ]


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
    history = serializers.HyperlinkedIdentityField(
        view_name="task-history-list",
        lookup_field="pk",
        lookup_url_kwarg="task_pk",
    )
    task_comments = serializers.HyperlinkedIdentityField(
        view_name="task-comments-list",
        lookup_field="pk",
        lookup_url_kwarg="task_pk",
    )
    project = serializers.HyperlinkedRelatedField(
        view_name="project-detail", read_only=True
    )
    created_by = serializers.HyperlinkedRelatedField(
        view_name="employee-detail", read_only=True
    )
    assigned_by = serializers.HyperlinkedRelatedField(
        view_name="employee-detail", read_only=True
    )
    assigned_to = serializers.HyperlinkedRelatedField(
        many=True, view_name="employee-detail", read_only=True
    )

    # Write-only relation fields
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
            "url",
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
            "assigned_by",
            "assigned_by_id",
            "assigned_to",
            "assigned_to_ids",
            "task_comments",
            "history",
        ]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class TaskHistorySerializer(serializers.ModelSerializer):
    history_user = serializers.StringRelatedField(read_only=True)
    history_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Task.history.model
        fields = "__all__"

    def get_changed_by(self, obj):
        return obj.history_user.username if obj.history_user else None
