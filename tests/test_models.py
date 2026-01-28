from django.test import TestCase
from django.contrib.auth.models import User
from organization.models import Employee


class EmployeeModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john',
            password='pass123'
        )

    def test_create_employee(self):
        employee = Employee.objects.create(user=self.user)
        self.assertEqual(employee.user.username, 'john')

    def test_supervisor_relationship(self):
        supervisor_user = User.objects.create_user(
            username='boss',
            password='pass123'
        )
        supervisor = Employee.objects.create(user=supervisor_user)

        employee = Employee.objects.create(
            user=self.user,
            supervisor=supervisor
        )

        self.assertEqual(employee.supervisor, supervisor)
