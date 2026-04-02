from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import User

class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/token/'
        self.me_url = '/api/auth/me/'
        self.logout_url = '/api/auth/logout/'
        self.change_password_url = '/api/auth/me/change-password/'
        self.update_profile_url = '/api/auth/me/update/'

        self.user_data = {
            'email': 'test@lumio.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }

    def get_tokens(self, email='test@lumio.com', password='StrongPass123!'):
        response = self.client.post(self.login_url, {
            'email': email,
            'password': password
        })
        return response.data

    def test_register_success(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'test@lumio.com')

    def test_register_duplicate_email(self):
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        data = self.user_data.copy()
        data['password2'] = 'WrongPass123!'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        data = self.user_data.copy()
        data['password'] = '123'
        data['password2'] = '123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        self.client.post(self.register_url, self.user_data)
        tokens = self.get_tokens()
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)

    def test_login_wrong_password(self):
        self.client.post(self.register_url, self.user_data)
        response = self.client.post(self.login_url, {
            'email': 'test@lumio.com',
            'password': 'WrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_me_authenticated(self):
        self.client.post(self.register_url, self.user_data)
        tokens = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@lumio.com')

    def test_get_me_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        self.client.post(self.register_url, self.user_data)
        tokens = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.patch(self.update_profile_url, {
            'first_name': 'Updated',
            'last_name': 'Name'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password(self):
        self.client.post(self.register_url, self.user_data)
        tokens = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.post(self.change_password_url, {
            'old_password': 'StrongPass123!',
            'new_password': 'NewStrongPass123!',
            'new_password2': 'NewStrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old(self):
        self.client.post(self.register_url, self.user_data)
        tokens = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.post(self.change_password_url, {
            'old_password': 'WrongPass123!',
            'new_password': 'NewStrongPass123!',
            'new_password2': 'NewStrongPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        self.client.post(self.register_url, self.user_data)
        tokens = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.post(self.logout_url, {
            'refresh': tokens['refresh']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)