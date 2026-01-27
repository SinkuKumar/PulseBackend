from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .views import (
    EmployeeViewSet,
    EmployeeHistoryViewSet,
    DesignationViewSet,
    LevelViewSet,
    LevelHistoryViewSet,
    DesignationHistoryViewSet,
)

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet)
router.register(r"designations", DesignationViewSet)
router.register(r"levels", LevelViewSet)
router.register(
    r"levels/(?P<level_pk>\d+)/history",
    LevelHistoryViewSet,
    basename="level-history",
)
router.register(
    r"designations/(?P<designation_pk>\d+)/history",
    DesignationHistoryViewSet,
    basename="designation-history",
)
router.register(
    r"employees/(?P<employee_pk>\d+)/history",
    EmployeeHistoryViewSet,
    basename="employee-history",
)


class OrganizationView(APIView):
    """
    Organization API root
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "employees": request.build_absolute_uri(reverse("employee-list")),
                "levels": request.build_absolute_uri(reverse("level-list")),
                "designation": request.build_absolute_uri(reverse("designation-list")),
            }
        )


urlpatterns = [
    path("", OrganizationView.as_view(), name="organization-root"),
    path("", include(router.urls)),
]
