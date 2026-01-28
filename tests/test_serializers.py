from django.test import TestCase
from django.contrib.auth.models import User
from organization.models import Employee
from organization.serializers import EmployeeSerializer


class EmployeeSerializerTest(TestCase):

    def test_create_employee_with_nested_user(self):
        data = {
            "user": {
                "username": "alice",
                "password": "secure123",
                "first_name": "Alice",
                "last_name": "Doe",
                "email": "alice@example.com"
            }
        }

        serializer = EmployeeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        employee = serializer.save()

        self.assertEqual(employee.user.username, "alice")
        self.assertTrue(employee.user.check_password("secure123"))

    def test_update_employee_user_fields(self):
        user = User.objects.create_user(
            username='bob',
            password='oldpass'
        )
        employee = Employee.objects.create(user=user)

        data = {
            "user": {
                "first_name": "Bob",
                "password": "newpass"
            }
        }

        serializer = EmployeeSerializer(employee, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        employee = serializer.save()
        employee.user.refresh_from_db()

        self.assertEqual(employee.user.first_name, "Bob")
        self.assertTrue(employee.user.check_password("newpass"))
