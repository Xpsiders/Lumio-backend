from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product, Category
from users.models import User

class ProductTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Smartphones', slug='smartphones')
        self.product = Product.objects.create(
            category=self.category,
            name='Lumio Pro X',
            slug='lumio-pro-x',
            description='Flagship phone',
            price=999.99,
            stock=50
        )

    def test_list_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_detail(self):
        response = self.client.get('/api/products/lumio-pro-x/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Lumio Pro X')

    def test_product_not_found(self):
        response = self.client.get('/api/products/non-existent/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_products(self):
        response = self.client.get('/api/products/?search=lumio')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_no_results(self):
        response = self.client.get('/api/products/?search=xyz')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filter_by_min_price(self):
        response = self.client.get('/api/products/?min_price=500')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_max_price(self):
        response = self.client.get('/api/products/?max_price=500')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_categories(self):
        response = self.client.get('/api/products/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_inactive_product_not_listed(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.get('/api/products/')
        self.assertEqual(len(response.data), 0)