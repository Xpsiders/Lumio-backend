from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer
from cart.models import Cart
from notifications.emails import send_order_confirmation_email, send_order_cancelled_email, send_seller_new_order_email


class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        if not cart.items.exists():
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # check stock for all items before creating order
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return Response(
                    {'detail': f'Not enough stock for {item.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # create the order
        order = Order.objects.create(
            user=request.user,
            shipping_address=serializer.validated_data['shipping_address'],
            total_price=cart.total
        )

        # snapshot each cart item into an order item
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.product.price,
                quantity=item.quantity
            )
            # deduct stock
            item.product.stock -= item.quantity
            item.product.save()

        # clear the cart after order is created
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    
        # after order is created, send confirmation email to buyer and notification email to sellers
        send_order_confirmation_email(order)

        # notify ch seller whose product are in the order
        seller_items = {}
        for item in order.items.all():
            if item.product and item.product.store:
                seller = item.product.store.owner
                if seller.id not in seller_items:
                    seller_items[seller.id] = {'seller': seller, 'items': []}
                seller_items[seller.id]['items'].append(item)

        for data in seller_items.values():
            send_seller_new_order_email(data['seller'], order, data['items'])

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)



class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.status not in ['pending', 'confirmed']:
            return Response(
                {'detail': 'Only pending or confirmed orders can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()

        order.status = 'cancelled'
        send_order_cancelled_email(order)

        return Response(OrderSerializer(order).data)


class AdminOrderUpdateView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all()

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)