from django.db import models
from django.conf import settings
from organization.models import Employee
from simple_history.models import HistoricalRecords


class Project(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    planned_start = models.DateField(null=True, blank=True)
    planned_end = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="project_created_by",
    )
    members = models.ManyToManyField(
        Employee, related_name="project_members", blank=True
    )
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.PROTECT)
    title = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    planned_start = models.DateField(null=True, blank=True)
    planned_end = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="task_created_by",
    )
    assigned_by = models.ForeignKey(
        Employee,
        related_name="task_assigned_by",
        on_delete=models.SET_NULL,
        null=True,
    )
    assigned_to = models.ManyToManyField(
        Employee, related_name="employee_assigned_to", blank=True
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("aborted", "Aborted"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.title} ({self.project.name})"
    

# class Comment(models.Model):
#     comment = models.TextField()
#     task = models.ManyToManyField(Task)
#     employee = models.ForeignKey(Employee, related_name="employee_comment", blank=True, on_delete=models.PROTECT)
#     commented_at = models.DateTimeField(auto_now_add=True)
