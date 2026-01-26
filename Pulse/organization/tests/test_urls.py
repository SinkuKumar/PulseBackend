from rest_framework.test import APITestCase
from rest_framework import status


class OrganizationRootTest(APITestCase):

    def test_organization_root(self):
        response = self.client.get('/api/v1/organization/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('employees', response.data)
