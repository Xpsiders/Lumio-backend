from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from products.models import Product, Category

class ReviewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='buyer@lumio.com',
            password='StrongPass123!'
        )
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.product = Product.objects.create(
            category=self.category,
            name='Lumio Watch',
            slug='lumio-watch',
            price=199.99,
            stock=30
        )
        tokens = self.client.post('/api/auth/token/', {
            'email': 'buyer@lumio.com',
            'password': 'StrongPass123!'
        }).data
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')

    def test_get_reviews(self):
        response = self.client.get(f'/api/reviews/{self.product.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 0)

    def test_create_review(self):
        response = self.client.post(f'/api/reviews/{self.product.slug}/', {
            'rating': 5,
            'title': 'Amazing product!',
            'body': 'Really love this watch.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)

    def test_duplicate_review(self):
        self.client.post(f'/api/reviews/{self.product.slug}/', {
            'rating': 5,
            'title': 'Amazing!',
            'body': 'Love it.'
        })
        response = self.client.post(f'/api/reviews/{self.product.slug}/', {
            'rating': 3,
            'title': 'Changed my mind',
            'body': 'Not so good.'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_rating(self):
        response = self.client.post(f'/api/reviews/{self.product.slug}/', {
            'rating': 6,
            'title': 'Too high',
            'body': 'Rating out of range.'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_review(self):
        create_response = self.client.post(f'/api/reviews/{self.product.slug}/', {
            'rating': 4,
            'title': 'Good',
            'body': 'Pretty good.'
        })
        review_id = create_response.data['id']
        response = self.client.delete(f'/api/reviews/detail/{review_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_reviews(self):
        self.client.post(f'/api/reviews/{self.product.slug}/', {
            'rating': 5,
            'title': 'Great!',
            'body': 'Love it.'
        })
        response = self.client.get('/api/reviews/my-reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)