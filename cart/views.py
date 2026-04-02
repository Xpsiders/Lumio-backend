from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_or_create_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get(self, request):
        cart = self.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart = self.get_or_create_cart(request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if product.stock < quantity:
            return Response({'detail': 'Not enough stock available'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        cart = self.get_or_create_cart(request.user)
        cart.items.all().delete()
        return Response({'detail': 'Cart cleared'}, status=status.HTTP_200_OK)


class CartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        quantity = int(request.data.get('quantity', item.quantity))
        if quantity < 1:
            return Response({'detail': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

        if item.product.stock < quantity:
            return Response({'detail': 'Not enough stock available'}, status=status.HTTP_400_BAD_REQUEST)

        item.quantity = quantity
        item.save()

        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)