from rest_framework import filters
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Employee, Designation, Level
from .serializers import (
    EmployeeSerializer,
    EmployeeHistorySerializer,
    DesignationSerializer,
    DesignationHistorySerializer,
    LevelSerializer,
    LevelHistorySerializer,
)

@extend_schema(tags=['Employee'])
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    ]
    ordering_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    ]


@extend_schema(tags=['Employee History'])
class EmployeeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmployeeHistorySerializer

    def get_queryset(self):
        return Employee.history.filter(id=self.kwargs["employee_pk"]).order_by(
            "-history_date"
        )


@extend_schema(tags=['Organization Designation'])
class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "description"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@extend_schema(tags=['Organization Designation History'])
class DesignationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DesignationHistorySerializer

    def get_queryset(self):
        return Designation.history.filter(id=self.kwargs["designation_pk"]).order_by(
            "-history_date"
        )


@extend_schema(tags=['Organization Level'])
class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]


@extend_schema(tags=['Organization Level History'])
class LevelHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LevelHistorySerializer

    def get_queryset(self):
        return Level.history.filter(id=self.kwargs["level_pk"]).order_by(
            "-history_date"
        )
