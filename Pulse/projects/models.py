from django.db import models
from organization.models import Employee


class Project(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    planned_start = models.DateField(null=True, blank=True)
    planned_end = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Employee,
        related_name="project_created_by",
        on_delete=models.PROTECT,
        null=True,
    )
    members = models.ManyToManyField(
        Employee, related_name="project_members", blank=True
    )

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
        Employee,
        related_name="task_created_by",
        on_delete=models.PROTECT,
        null=True,
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

    # Time tracking (in hours)
    planned_time = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Planned time in hours",
    )

    actual_time = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual time spent in hours",
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("aborted", "Aborted"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.title} ({self.project.name})"
    

class Comment(models.Model):
    comment = models.TextField()
    task = models.ManyToManyField(Task)
    employee = models.ForeignKey(Employee, related_name="employee_comment", blank=True, on_delete=models.PROTECT)
    commented_at = models.DateTimeField(auto_now_add=True)
