import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from organization.models import Employee
from .models import Project, Task, Comment

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(username="testuser", password="password")
    # Assuming Employee has a one-to-one or FK to User
    Employee.objects.create(user=user, name="Test Employee")
    return user

@pytest.fixture
def project(test_user):
    return Project.objects.create(name="Test Project", created_by=test_user)

@pytest.fixture
def task(project, test_user):
    return Task.objects.create(project=project, title="Initial Task", created_by=test_user)

### --- Project Tests ---

@pytest.mark.django_db
class TestProjectAPI:
    def test_create_project(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        url = reverse('project-list')
        data = {"name": "New Project", "description": "A test project"}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == "New Project"
        # Verify created_by is set automatically in Serializer.create
        assert Project.objects.get(name="New Project").created_by == test_user

    def test_project_history_viewset(self, api_client, test_user, project):
        api_client.force_authenticate(user=test_user)
        # Update project to trigger history
        project.name = "Updated Name"
        project.save()
        
        url = reverse('project-history-list', kwargs={'project_pk': project.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2  # Initial + Update

### --- Task Tests ---

@pytest.mark.django_db
class TestTaskAPI:
    def test_create_task_with_assignments(self, api_client, test_user, project):
        api_client.force_authenticate(user=test_user)
        employee = Employee.objects.get(user=test_user)
        url = reverse('task-list')
        
        data = {
            "project": reverse('project-detail', args=[project.pk]),
            "title": "Task with IDs",
            "assigned_by_id": employee.id,
            "assigned_to_ids": [employee.id]
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == "Task with IDs"

    def test_task_filtering(self, api_client, test_user, task):
        api_client.force_authenticate(user=test_user)
        url = reverse('task-list')
        
        # Test status filter
        response = api_client.get(f"{url}?status=pending")
        assert len(response.data) == 1
        
        response = api_client.get(f"{url}?status=completed")
        assert len(response.data) == 0

### --- Comment Tests ---

@pytest.mark.django_db
class TestCommentAPI:
    def test_create_comment_validation(self, api_client, test_user, task):
        api_client.force_authenticate(user=test_user)
        url = reverse('task-comments-list', kwargs={'task_pk': task.pk})
        
        data = {"comment": "This is a test comment"}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['comment'] == "This is a test comment"

    def test_comment_fails_without_employee_profile(self, api_client, db):
        # User without an associated Employee record
        user_no_emp = User.objects.create_user(username="noemp", password="password")
        task_obj = Task.objects.create(title="No Emp Task", project=Project.objects.create(name="P1"))
        
        api_client.force_authenticate(user=user_no_emp)
        url = reverse('task-comments-list', kwargs={'task_pk': task_obj.pk})
        
        response = api_client.post(url, {"comment": "Should fail"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Only employees can comment" in str(response.data)