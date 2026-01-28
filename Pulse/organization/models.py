from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from simple_history.models import HistoricalRecords


class Designation(models.Model):
    title = models.CharField("Title", max_length=255)
    level = models.CharField("Level", blank=True)
    description = models.TextField("Description", blank=True)
    created_on = models.DateTimeField("Created on", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="designation_created_by",
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.title


class Level(models.Model):
    level = models.IntegerField("Level")
    description = models.TextField("Level Description")
    created_on = models.DateTimeField("Created on", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="levels_created",
    )
    history = HistoricalRecords()

    def __str__(self):
        return str(f"Level - {self.level}")


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="employee")
    employee_id = models.IntegerField(unique=True, null=True)

    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    supervisor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="report_to",
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.user.get_full_name() or self.user.username
