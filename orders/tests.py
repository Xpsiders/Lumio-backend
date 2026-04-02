from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from products.models import Product, Category
from cart.models import Cart, CartItem

class OrderTestCase(TestCase):
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

        # add item to cart
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

    def test_create_order(self):
        response = self.client.post('/api/orders/create/', {
            'shipping_address': '123 Lagos Street, Nigeria'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')

    def test_create_order_empty_cart(self):
        from cart.models import Cart
        Cart.objects.filter(user=self.user).delete()
        response = self.client.post('/api/orders/create/', {
            'shipping_address': '123 Lagos Street, Nigeria'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders(self):
        self.client.post('/api/orders/create/', {
            'shipping_address': '123 Lagos Street, Nigeria'
        })
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_cancel_order(self):
        order_response = self.client.post('/api/orders/create/', {
            'shipping_address': '123 Lagos Street, Nigeria'
        })
        order_id = order_response.data['id']
        response = self.client.post(f'/api/orders/{order_id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')

    def test_stock_deducted_after_order(self):
        self.client.post('/api/orders/create/', {
            'shipping_address': '123 Lagos Street, Nigeria'
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)  # was 10, ordered 2

    def test_cart_cleared_after_order(self):
        self.client.post('/api/orders/create/', {
            'shipping_address': '123 Lagos Street, Nigeria'
        })
        response = self.client.get('/api/cart/')
        self.assertEqual(response.data['item_count'], 0)

    def test_orders_require_auth(self):
        self.client.credentials()
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)