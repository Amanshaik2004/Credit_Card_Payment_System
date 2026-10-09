from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.profile_url = reverse('accounts:profile')

        self.user_data = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertEqual(response.data['user']['username'], 'john_doe')
        self.assertEqual(response.data['user']['email'], 'john@example.com')

        # Verify password is encrypted, NOT plain text
        user = User.objects.get(username='john_doe')
        self.assertNotEqual(user.password, 'SecurePassword123!')
        self.assertTrue(user.check_password('SecurePassword123!'))

    def test_registration_password_mismatch(self):
        data = self.user_data.copy()
        data['password_confirm'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_registration_duplicate_email(self):
        self.client.post(self.register_url, self.user_data, format='json')
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'another_user'
        response = self.client.post(self.register_url, duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_login_success_with_username(self):
        # Register first
        self.client.post(self.register_url, self.user_data, format='json')

        login_data = {
            'username': 'john_doe',
            'password': 'SecurePassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_user_login_success_with_email(self):
        self.client.post(self.register_url, self.user_data, format='json')

        login_data = {
            'username': 'john@example.com',
            'password': 'SecurePassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_user_login_invalid_password(self):
        self.client.post(self.register_url, self.user_data, format='json')

        login_data = {
            'username': 'john_doe',
            'password': 'WrongPassword999!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protected_profile_route_requires_auth(self):
        # Without token -> 401
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_profile_route_success(self):
        reg_resp = self.client.post(self.register_url, self.user_data, format='json')
        token = reg_resp.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'john_doe')

    def test_user_logout(self):
        reg_resp = self.client.post(self.register_url, self.user_data, format='json')
        access_token = reg_resp.data['tokens']['access']
        refresh_token = reg_resp.data['tokens']['refresh']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_resp = self.client.post(self.logout_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)
