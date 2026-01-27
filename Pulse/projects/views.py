from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Project
from .serializers import ProjectSerializer

from .models import Task
from .serializers import TaskSerializer


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
