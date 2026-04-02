from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer, CreateReviewSerializer
from products.models import Product
from orders.models import Order

class ProductReviewsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(product=product).select_related('user')
        serializer = ReviewSerializer(reviews, many=True)

        return Response({
            'average_rating': product.average_rating,
            'review_count': product.review_count,
            'reviews': serializer.data
        })

    def post(self, request, slug):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            product = Product.objects.get(slug=slug, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # check if user already reviewed this product
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response({'detail': 'You have already reviewed this product'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CreateReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # check if verified purchase
        is_verified = Order.objects.filter(
            user=request.user,
            status__in=['confirmed', 'shipped', 'delivered'],
            items__product=product
        ).exists()

        review = serializer.save(
            product=product,
            user=request.user,
            is_verified_purchase=is_verified
        )

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class ReviewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            review = Review.objects.get(id=pk, user=request.user)
        except Review.DoesNotExist:
            return Response({'detail': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ReviewSerializer(review).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            review = Review.objects.get(id=pk, user=request.user)
        except Review.DoesNotExist:
            return Response({'detail': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response({'detail': 'Review deleted'}, status=status.HTTP_200_OK)


class UserReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('product')