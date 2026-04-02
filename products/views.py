from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .filters import ProductFilter
from stores.permissions import IsApprovedSeller

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()

class SellerProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsApprovedSeller]

    def get_queryset(self):
        return Product.objects.filter(store=self.request.user.store)

class SellerProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsApprovedSeller]

    def perform_create(self, serializer):
        from django.utils.text import slugify
        name = serializer.validated_data['name']
        serializer.save(store=self.request.user.store, slug=slugify(name))

class SellerProductUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsApprovedSeller]
    lookup_field = 'slug'

    def get_queryset(self):
        # sellers can only edit their own products
        return Product.objects.filter(store=self.request.user.store)

        
class AdminProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminProductUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'
    queryset = Product.objects.all()