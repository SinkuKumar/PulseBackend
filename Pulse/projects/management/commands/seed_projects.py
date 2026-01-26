import random
from datetime import timedelta, date

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now

from projects.models import Project, Task
from organization.models import Employee


class Command(BaseCommand):
    help = "Seed projects and tasks with dummy data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--projects",
            type=int,
            default=1,
            help="Number of projects to create",
        )

        parser.add_argument(
            "--tasks-per-project",
            type=int,
            default=5,
            help="Number of tasks per project",
        )

        parser.add_argument(
            "--default-project",
            action="store_true",
            help="Create or reuse a default project",
        )

        parser.add_argument(
            "--default-project-name",
            type=str,
            default="Default Project",
            help="Name of the default project",
        )

    def handle(self, *args, **options):
        employees = list(Employee.objects.all())
        if not employees:
            raise CommandError("No employees found. Seed employees first.")

        projects_count = options["projects"]
        tasks_per_project = options["tasks_per_project"]

        if options["default_project"]:
            project = self._get_or_create_default_project(
                name=options["default_project_name"],
                employees=employees,
            )
            self._create_tasks(project, tasks_per_project, employees)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Default project '{project.name}' seeded with {tasks_per_project} tasks"
                )
            )
            return

        for i in range(projects_count):
            project = self._create_project(i + 1, employees)
            self._create_tasks(project, tasks_per_project, employees)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {projects_count} project(s) with {tasks_per_project} task(s) each"
            )
        )

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    def _get_or_create_default_project(self, name, employees):
        project, created = Project.objects.get_or_create(
            name=name,
            defaults=self._project_defaults(employees),
        )

        if created:
            project.members.set(employees)

        return project

    def _create_project(self, index, employees):
        project = Project.objects.create(
            name=f"Project {index}",
            **self._project_defaults(employees),
        )
        project.members.set(random.sample(employees, k=min(3, len(employees))))
        return project

    def _project_defaults(self, employees):
        start = date.today()
        end = start + timedelta(days=30)

        return {
            "description": "Auto-generated project",
            "planned_start": start,
            "planned_end": end,
            "actual_start": start,
            "created_by": random.choice(employees),
        }

    def _create_tasks(self, project, count, employees):
        for i in range(count):
            creator = random.choice(employees)
            assignees = random.sample(employees, k=min(2, len(employees)))

            task = Task.objects.create(
                project=project,
                title=f"Task {i + 1} - {project.name}",
                description="Auto-generated task",
                planned_start=project.planned_start,
                planned_end=project.planned_start + timedelta(days=7),
                planned_time=8,
                actual_time=random.randint(1, 8),
                status=random.choice(["todo", "in_progress", "done"]),
                created_by=creator,
                assigned_by=creator,
            )

            task.assigned_to.set(assignees)
