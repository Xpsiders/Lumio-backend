from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal', 'added_at')

    def validate_product_id(self, value):
        from products.models import Product
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Product not found or unavailable')
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be at least 1')
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'item_count', 'updated_at')