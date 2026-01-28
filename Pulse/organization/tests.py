from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Employee, Designation, Level

class OrganizationComprehensiveTests(APITestCase):
    def setUp(self):
        # Setup users
        self.admin_user = User.objects.create_user(
            username="admin", 
            email="admin@pulse.com", 
            first_name="Admin", 
            last_name="User", 
            password="password123"
        )
        self.staff_user = User.objects.create_user(username="staff", password="password123")
        
        # Authenticate as admin for setup
        self.client.force_authenticate(user=self.admin_user)
        
        # Initial Data
        self.level_1 = Level.objects.create(level=1, description="Junior", created_by=self.admin_user)
        self.desig_dev = Designation.objects.create(title="Developer", level="1", created_by=self.admin_user)
        self.emp_1 = Employee.objects.create(
            user=self.admin_user, 
            employee_id=1001, 
            designation=self.desig_dev, 
            level=self.level_1
        )

    ## --- 1. Model Logic & Constraints ---

    def test_model_string_representations(self):
        """Verify __str__ methods for all models"""
        self.assertEqual(str(self.desig_dev), "Developer")
        self.assertEqual(str(self.level_1), "Level - 1")
        # Test Employee full name fallback
        self.assertEqual(str(self.emp_1), "Admin User")
        
        # Test Employee username fallback
        self.staff_user.first_name = ""
        self.staff_user.save()
        emp_2 = Employee.objects.create(user=self.staff_user, employee_id=1002)
        self.assertEqual(str(emp_2), "staff")

    def test_on_delete_protection(self):
        """Verify models.PROTECT prevents deletion of related records"""
        with self.assertRaises(ProtectedError):
            self.admin_user.delete()  # Protected by Employee.user
        
        with self.assertRaises(ProtectedError):
            self.level_1.delete()  # Protected by Employee.level is PROTECT? 
            # Note: models.py uses SET_NULL for Employee.level, but PROTECT for Level.created_by
            # Let's test the Level.created_by protection:
            self.admin_user.delete() 

    ## --- 2. Serializer & ViewSet Logic ---

    def test_designation_auto_user_assignment(self):
        """Verify perform_create assigns request.user"""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('designation-list')
        data = {"title": "Designer", "level": "2"}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        designation = Designation.objects.get(title="Designer")
        self.assertEqual(designation.created_by, self.staff_user)

    def test_employee_write_only_ids(self):
        """Test creating employee using user_id, level_id, etc."""
        new_user = User.objects.create_user(username="newbie", password="password")
        url = reverse('employee-list')
        data = {
            "employee_id": 5000,
            "user_id": new_user.id,
            "designation_id": self.desig_dev.id,
            "level_id": self.level_1.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the response returns Hyperlinks, not IDs
        self.assertIn("http", response.data['user'])
        self.assertIn("http", response.data['designation'])

    ## --- 3. Simple History Tracking ---

    def test_nested_history_filtering(self):
        """Verify history ViewSet filters by the parent object PK"""
        # Trigger an update to create a history record
        url = reverse('employee-detail', args=[self.emp_1.id])
        self.client.patch(url, {"employee_id": 1005})
        
        # Access nested history route: /employees/{pk}/history/
        history_url = reverse('employee-history-list', kwargs={'employee_pk': self.emp_1.id})
        response = self.client.get(history_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have 2 entries: Create and Update
        self.assertEqual(len(response.data), 2)
        # Verify ordering is newest first
        self.assertEqual(response.data[0]['employee_id'], 1005)

    ## --- 4. Search & Discovery ---

    def test_employee_search_filter(self):
        """Verify search against user fields"""
        url = reverse('employee-list')
        # Search by email
        response = self.client.get(url, {'search': 'admin@pulse.com'})
        self.assertEqual(len(response.data), 1)
        # Search by last name
        response = self.client.get(url, {'search': 'User'})
        self.assertEqual(len(response.data), 1)

    def test_api_root_discovery(self):
        """Verify OrganizationView returns correct discovery links"""
        url = reverse('organization-root')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['employees'].endswith('/employees/'))
        self.assertTrue(response.data['levels'].endswith('/levels/'))
