from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Store
from .serializers import StoreSerializer, CreateStoreSerializer
from .permissions import IsSeller, IsStoreOwner
from orders.models import Order, OrderItem
from products.models import Product
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from .permissions import IsApprovedSeller
from notifications.emails import send_store_approved_email, send_store_suspended_email


class RegisterStoreView(generics.CreateAPIView):
    serializer_class = CreateStoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # upgrade user role to seller on store registration
        user = self.request.user
        user.role = 'seller'
        user.save()
        serializer.save()

class StoreDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = StoreSerializer
    permission_classes = [IsSeller, IsStoreOwner]
    lookup_field = 'slug'
    queryset = Store.objects.all()

class PublicStoreListView(generics.ListAPIView):
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Store.objects.filter(status='approved')

class PublicStoreDetailView(generics.RetrieveAPIView):
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    queryset = Store.objects.filter(status='approved')


class SellerOrdersView(APIView):
    permission_classes = [IsApprovedSeller]

    def get(self, request):
        store = request.user.store

        # get all order items belonging to this seller's products
        order_items = OrderItem.objects.filter(
            product__store=store
        ).select_related('order', 'product').order_by('-order__created_at')

        # group by order
        orders_data = {}
        for item in order_items:
            order_id = str(item.order.id)
            if order_id not in orders_data:
                orders_data[order_id] = {
                    'order_id': order_id,
                    'status': item.order.status,
                    'customer_email': item.order.user.email,
                    'created_at': item.order.created_at,
                    'items': [],
                    'order_total': 0
                }
            orders_data[order_id]['items'].append({
                'product_name': item.product_name,
                'quantity': item.quantity,
                'price': str(item.product_price),
                'subtotal': str(item.subtotal)
            })
            orders_data[order_id]['order_total'] += float(item.subtotal)

        return Response(list(orders_data.values()))


class SellerStatsView(APIView):
    permission_classes = [IsApprovedSeller]

    def get(self, request):
        store = request.user.store
        now = timezone.now()

        # all order items for this seller
        all_items = OrderItem.objects.filter(
            product__store=store,
            order__status__in=['confirmed', 'shipped', 'delivered']
        )

        # this week
        week_start = now - timedelta(days=7)
        week_items = all_items.filter(order__created_at__gte=week_start)

        # this month
        month_start = now - timedelta(days=30)
        month_items = all_items.filter(order__created_at__gte=month_start)

        def calc_revenue(queryset):
            total = sum(item.subtotal for item in queryset)
            return float(total)

        # best selling products
        best_sellers = Product.objects.filter(store=store).annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:5].values('name', 'total_sold', 'price', 'stock')

        # low stock alerts (less than 10 units)
        low_stock = Product.objects.filter(
            store=store,
            stock__lt=10,
            is_active=True
        ).values('name', 'stock', 'slug')

        return Response({
            'store': store.name,
            'revenue': {
                'total': calc_revenue(all_items),
                'this_month': calc_revenue(month_items),
                'this_week': calc_revenue(week_items),
            },
            'orders': {
                'total': all_items.values('order').distinct().count(),
                'this_month': month_items.values('order').distinct().count(),
                'this_week': week_items.values('order').distinct().count(),
            },
            'products': {
                'total': Product.objects.filter(store=store).count(),
                'active': Product.objects.filter(store=store, is_active=True).count(),
                'low_stock': low_stock,
                'best_sellers': list(best_sellers),
            }
        })


class SellerProductStatsView(APIView):
    permission_classes = [IsApprovedSeller]

    def get(self, request):
        store = request.user.store

        products = Product.objects.filter(store=store).annotate(
            total_sold=Sum('orderitem__quantity'),
            total_revenue=Sum(
                F('orderitem__quantity') * F('orderitem__product_price')
            )
        ).values(
            'name', 'slug', 'price', 'stock',
            'is_active', 'total_sold', 'total_revenue'
        ).order_by('-total_sold')

        return Response(list(products))

        

class AdminStoreApprovalView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            store = Store.objects.get(id=pk)
        except Store.DoesNotExist:
            return Response({'detail': 'Store not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in ['approved', 'suspended', 'pending']:
            return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        store.status = new_status
        store.save()

        if new_status == 'approved':
            send_store_approved_email(store)
        elif new_status == 'suspended':
            send_store_suspended_email(store)

        return Response(StoreSerializer(store).data)