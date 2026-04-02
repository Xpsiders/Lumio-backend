from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from users.models import User
from products.models import Product, Category
from cart.models import Cart, CartItem
from orders.models import Order

class PaymentTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='buyer@lumio.com',
            password='StrongPass123!'
        )
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.product = Product.objects.create(
            category=self.category,
            name='Lumio Pro',
            slug='lumio-pro',
            price=499.99,
            stock=10
        )
        tokens = self.client.post('/api/auth/token/', {
            'email': 'buyer@lumio.com',
            'password': 'StrongPass123!'
        }).data
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')

        # create order directly
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        order_response = self.client.post('/api/orders/create/', {
            'shipping_address': '123 Lagos Street, Nigeria'
        })
        self.order_id = order_response.data['id']

    def test_get_payment_config(self):
        self.client.credentials()  # no auth needed
        response = self.client.get('/api/payments/config/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('public_key', response.data)

    @patch('payments.views.requests.post')
    def test_initialize_payment(self, mock_post):
        # mock Paystack API response
        mock_post.return_value = MagicMock(
            json=lambda: {
                'status': True,
                'data': {
                    'authorization_url': 'https://checkout.paystack.com/test',
                    'access_code': 'test_access_code',
                    'reference': str(self.order_id)
                }
            }
        )

        response = self.client.post('/api/payments/initialize/', {
            'order_id': self.order_id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('authorization_url', response.data)
        self.assertIn('reference', response.data)

    @patch('payments.views.requests.post')
    def test_initialize_payment_invalid_order(self, mock_post):
        response = self.client.post('/api/payments/initialize/', {
            'order_id': '00000000-0000-0000-0000-000000000000'
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_initialize_payment_requires_auth(self):
        self.client.credentials()
        response = self.client.post('/api/payments/initialize/', {
            'order_id': self.order_id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('payments.views.requests.get')
    def test_verify_payment_success(self, mock_get):
        # mock successful Paystack verification
        mock_get.return_value = MagicMock(
            json=lambda: {
                'status': True,
                'data': {
                    'status': 'success',
                    'metadata': {
                        'order_id': str(self.order_id)
                    }
                }
            }
        )

        response = self.client.get(f'/api/payments/verify/{self.order_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

        # check order status updated to confirmed
        order = Order.objects.get(id=self.order_id)
        self.assertEqual(order.status, 'confirmed')

    @patch('payments.views.requests.get')
    def test_verify_payment_failed(self, mock_get):
        # mock failed Paystack verification
        mock_get.return_value = MagicMock(
            json=lambda: {
                'status': True,
                'data': {
                    'status': 'failed',
                    'metadata': {
                        'order_id': str(self.order_id)
                    }
                }
            }
        )

        response = self.client.get(f'/api/payments/verify/{self.order_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'failed')

        # order should still be pending
        order = Order.objects.get(id=self.order_id)
        self.assertEqual(order.status, 'pending')

    def test_initialize_confirmed_order(self):
        # confirmed orders should not be payable again
        Order.objects.filter(id=self.order_id).update(status='confirmed')
        response = self.client.post('/api/payments/initialize/', {
            'order_id': self.order_id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)