from rest_framework import filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Employee, Designation, Level
from .serializers import (
    EmployeeSerializer,
    EmployeeHistorySerializer,
    DesignationSerializer,
    DesignationHistorySerializer,
    LevelSerializer,
    LevelHistorySerializer,
)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
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


class EmployeeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmployeeHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Employee.history.filter(id=self.kwargs["employee_pk"]).order_by(
            "-history_date"
        )


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "description"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DesignationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DesignationHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Designation.history.filter(id=self.kwargs["designation_pk"]).order_by(
            "-history_date"
        )


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]


class LevelHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LevelHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Level.history.filter(id=self.kwargs["level_pk"]).order_by(
            "-history_date"
        )
