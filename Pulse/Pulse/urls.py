"""
URL configuration for Pulse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


class PulseRootSerializer(serializers.Serializer):
    """
    Hypermedia links to top-level Pulse services.
    """
    Users = serializers.URLField(help_text="Users service root")
    Organization = serializers.URLField(help_text="Organization service root")
    Projects = serializers.URLField(help_text="Projects service root")


@extend_schema(
    tags=["API Discovery"],
    summary="Pulse API root",
    description="Discoverable entry point for Pulse services.",
    responses=PulseRootSerializer,
)
class PulseView(APIView):
    """
    Provides discoverable entry points
    """
    permission_classes = [AllowAny]
    serializer_class = PulseRootSerializer

    def get(self, request, *args, **kwargs):
        return Response({
            "Users": request.build_absolute_uri(reverse("user-root")),
            "Organization": request.build_absolute_uri(reverse("organization-root")),
            "Projects": request.build_absolute_uri(reverse("projects-root")),
        })


urlpatterns = [
    path("", PulseView.as_view(), name="api-root"),
    path("admin/", admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path("api/v1/users/", include(("users.urls"))),
    path("api/v1/organization/", include(("organization.urls"))),
    path("api/v1/projects/", include(("projects.urls"))),

    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
