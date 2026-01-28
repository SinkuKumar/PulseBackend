from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from organization.models import Employee


class EmployeeAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            password='pass123'
        )
        self.employee = Employee.objects.create(user=self.user)

        self.client.login(username='apiuser', password='pass123')

    def test_list_employees_authenticated(self):
        response = self.client.get('/api/v1/organization/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_employee(self):
        data = {
            "user": {
                "username": "newuser",
                "password": "newpass123"
            }
        }

        response = self.client.post('/api/v1/organization/employees/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username="newuser").count(), 1)

    def test_unauthenticated_access_denied(self):
        self.client.logout()
        response = self.client.get('/api/v1/organization/employees/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
