from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from stores.models import Store

class StoreTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # create a regular user
        self.user = User.objects.create_user(
            email='seller@lumio.com',
            password='StrongPass123!'
        )

        # create an admin user
        self.admin = User.objects.create_superuser(
            email='admin@lumio.com',
            password='StrongPass123!'
        )

        # get user tokens
        tokens = self.client.post('/api/auth/token/', {
            'email': 'seller@lumio.com',
            'password': 'StrongPass123!'
        }).data
        self.user_token = tokens['access']

        # get admin tokens
        admin_tokens = self.client.post('/api/auth/token/', {
            'email': 'admin@lumio.com',
            'password': 'StrongPass123!'
        }).data
        self.admin_token = admin_tokens['access']

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_register_store(self):
        self.authenticate(self.user_token)
        response = self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Store.objects.count(), 1)

    def test_register_store_upgrades_role(self):
        self.authenticate(self.user_token)
        self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'seller')

    def test_register_store_requires_auth(self):
        response = self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_store_starts_as_pending(self):
        self.authenticate(self.user_token)
        self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })
        store = Store.objects.first()
        self.assertEqual(store.status, 'pending')

    def test_admin_approve_store(self):
        self.authenticate(self.user_token)
        self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })
        store = Store.objects.first()

        self.authenticate(self.admin_token)
        response = self.client.patch(f'/api/stores/admin/{store.id}/approval/', {
            'status': 'approved'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        store.refresh_from_db()
        self.assertEqual(store.status, 'approved')

    def test_admin_suspend_store(self):
        self.authenticate(self.user_token)
        self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })
        store = Store.objects.first()

        self.authenticate(self.admin_token)
        response = self.client.patch(f'/api/stores/admin/{store.id}/approval/', {
            'status': 'suspended'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        store.refresh_from_db()
        self.assertEqual(store.status, 'suspended')

    def test_non_admin_cannot_approve_store(self):
        self.authenticate(self.user_token)
        self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })
        store = Store.objects.first()

        response = self.client.patch(f'/api/stores/admin/{store.id}/approval/', {
            'status': 'approved'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_store_list_shows_approved_only(self):
        self.authenticate(self.user_token)
        self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })

        # store is pending — should not show in public list
        response = self.client.get('/api/stores/')
        self.assertEqual(len(response.data), 0)

        # approve the store
        store = Store.objects.first()
        self.authenticate(self.admin_token)
        self.client.patch(f'/api/stores/admin/{store.id}/approval/', {
            'status': 'approved'
        })

        # now it should show
        response = self.client.get('/api/stores/')
        self.assertEqual(len(response.data), 1)

    def test_invalid_status_rejected(self):
        self.authenticate(self.user_token)
        self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })
        store = Store.objects.first()

        self.authenticate(self.admin_token)
        response = self.client.patch(f'/api/stores/admin/{store.id}/approval/', {
            'status': 'invalid_status'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unapproved_seller_cannot_add_products(self):
        self.authenticate(self.user_token)
        self.client.post('/api/stores/register/', {
            'name': 'Tech Haven',
            'description': 'Best tech gadgets'
        })
        response = self.client.post('/api/products/seller/create/', {
            'name': 'Test Product',
            'price': 99.99,
            'stock': 10,
            'description': 'A test product'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)