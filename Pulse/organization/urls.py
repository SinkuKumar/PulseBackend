from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .views import EmployeeViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)


class OrganizationView(APIView):
    """
    Organization API root
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "employees": request.build_absolute_uri(reverse("employee-list")),
        })


urlpatterns = [
    path('', OrganizationView.as_view(), name="organization-root"),
    path('', include(router.urls))
]
