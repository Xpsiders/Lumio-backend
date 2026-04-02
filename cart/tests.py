from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from products.models import Product, Category

class CartTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='buyer@lumio.com',
            password='StrongPass123!'
        )
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.product = Product.objects.create(
            category=self.category,
            name='Lumio Lite',
            slug='lumio-lite',
            price=299.99,
            stock=20
        )
        tokens = self.client.post('/api/auth/token/', {
            'email': 'buyer@lumio.com',
            'password': 'StrongPass123!'
        }).data
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')

    def test_get_empty_cart(self):
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_count'], 0)

    def test_add_item_to_cart(self):
        response = self.client.post('/api/cart/', {
            'product_id': str(self.product.id),
            'quantity': 2
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_count'], 1)

    def test_add_invalid_product(self):
        response = self.client.post('/api/cart/', {
            'product_id': '00000000-0000-0000-0000-000000000000',
            'quantity': 1
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_exceeds_stock(self):
        response = self.client.post('/api/cart/', {
            'product_id': str(self.product.id),
            'quantity': 999
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clear_cart(self):
        self.client.post('/api/cart/', {
            'product_id': str(self.product.id),
            'quantity': 1
        })
        response = self.client.delete('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cart_requires_auth(self):
        self.client.credentials()
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)