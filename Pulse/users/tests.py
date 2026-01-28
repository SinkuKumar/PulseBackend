from django.urls import reverse
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APITestCase

class UserModuleTests(APITestCase):

    def setUp(self):
        # Create a sample group and user for testing
        self.group = Group.objects.create(name="Managers")
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        self.user = User.objects.create_user(
            username="existinguser", 
            email="existing@example.com", 
            password="password123"
        )

    ## --- Serializer & ViewSet Tests ---

    def test_create_user(self):
        """Test creating a user via POST and ensuring password hashing."""
        url = reverse('user-list')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user exists in DB
        new_user = User.objects.get(username="testuser")
        self.assertEqual(new_user.email, "test@example.com")
        
        # Verify password is not in response but is hashed in DB
        self.assertNotIn('password', response.data)
        self.assertTrue(new_user.check_password("securepassword123"))

    def test_update_user_password(self):
        """Test the custom update method in UserSerializer."""
        url = reverse('user-detail', args=[self.user.id])
        update_data = {"password": "newsecretpassword123"}
        
        # Patch request to update only password
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newsecretpassword123"))

    def test_user_filtering(self):
        """Test that DjangoFilterBackend works for the UserViewSet."""
        url = reverse('user-list')
        response = self.client.get(url, {'username': 'existinguser'})
        
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'existinguser')

    ## --- Group Tests ---

    def test_group_list(self):
        """Test retrieving the list of groups."""
        url = reverse('group-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Managers")

    ## --- Root View Tests ---

    def test_api_root(self):
        """Test the custom UserView root endpoint."""
        url = reverse('user-root')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('users', response.data)
        self.assertIn('groups', response.data)