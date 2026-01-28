from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from organization.models import Employee
from .models import Project, Task, Comment
from .serializers import (
    TaskSerializer,
    TaskHistorySerializer,
    ProjectSerializer,
    ProjectHistorySerializer,
    CommentSerializer,
)


@extend_schema(tags=["Project"])
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "planned_start",
        "planned_end",
        "actual_start",
        "actual_end",
        "created_by",
        "members",
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
        "planned_start",
        "planned_end",
        "actual_start",
        "actual_end",
        "created_at",
    ]


@extend_schema(tags=["Project History"])
class ProjectHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectHistorySerializer

    def get_queryset(self):
        return Project.history.filter(id=self.kwargs["project_pk"]).order_by(
            "-history_date"
        )


@extend_schema(tags=["Task"])
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "project",
        "status",
        "planned_start",
        "planned_end",
        "actual_start",
        "actual_end",
        "created_by",
        "assigned_by",
        "assigned_to",
    ]

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "title",
        "status",
        "planned_start",
        "planned_end",
        "actual_start",
        "actual_end",
        "created_at",
        "planned_time",
        "actual_time",
    ]


@extend_schema(tags=["Task History"])
class TaskHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaskHistorySerializer

    def get_queryset(self):
        return Task.history.filter(id=self.kwargs["task_pk"]).order_by("-history_date")


@extend_schema(tags=["Task Comment"])
class TaskCommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_pk"])

    def perform_create(self, serializer):
        if not hasattr(self.request.user, "employee"):
            raise ValidationError("Only employees can comment")

        serializer.save(
            task_id=self.kwargs["task_pk"],
            created_by=self.request.user.employee,
        )
