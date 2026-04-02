from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'status', 'shipping_address', 'total_price',
            'items', 'stripe_payment_intent', 'created_at', 'updated_at'
        )
        read_only_fields = ('status', 'total_price', 'stripe_payment_intent')


class CreateOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()