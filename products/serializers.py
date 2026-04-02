from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False)
    in_stock = serializers.BooleanField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'category', 'category_id', 'name', 'slug',
            'description', 'price', 'stock', 'in_stock',
            'image', 'is_active', 'created_at',
            'average_rating', 'review_count'
        )