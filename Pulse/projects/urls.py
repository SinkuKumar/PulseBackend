from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema

from .views import (
    ProjectViewSet,
    ProjectHistoryViewSet,
    TaskViewSet,
    TaskHistoryViewSet,
    TaskCommentViewSet,
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"tasks", TaskViewSet)
router.register(
    r"projects/(?P<project_pk>\d+)/history",
    ProjectHistoryViewSet,
    basename="project-history",
)
router.register(
    r"tasks/(?P<task_pk>\d+)/history",
    TaskHistoryViewSet,
    basename="task-history",
)
router.register(
    r"tasks/(?P<task_pk>\d+)/comments",
    TaskCommentViewSet,
    basename="task-comments",
)


@extend_schema(
    tags=["API Discovery"],
    summary="Pulse API root",
    description="Discoverable entry point for Pulse services.",
    responses=ProjectHistoryViewSet,
)
class ProjectView(APIView):
    """
    Project API root
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "projects": request.build_absolute_uri(reverse("project-list")),
                "tasks": request.build_absolute_uri(reverse("task-list")),
            }
        )


urlpatterns = [
    path("", ProjectView.as_view(), name="projects-root"),
    path("", include(router.urls)),
]
