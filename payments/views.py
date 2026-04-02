import hmac
import hashlib
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from orders.models import Order
import requests

PAYSTACK_BASE_URL = 'https://api.paystack.co'

def paystack_headers():
    return {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

class InitializePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'pending':
            return Response({'detail': 'Order is not payable'}, status=status.HTTP_400_BAD_REQUEST)

        # initialize transaction with Paystack
        payload = {
            'email': request.user.email,
            'amount': int(order.total_price * 100),  # Paystack uses kobo
            'reference': str(order.id),              # use order ID as reference
            'metadata': {
                'order_id': str(order.id),
                'user_id': str(request.user.id),
            }
        }

        response = requests.post(
            f'{PAYSTACK_BASE_URL}/transaction/initialize',
            headers=paystack_headers(),
            json=payload
        )

        data = response.json()

        if not data.get('status'):
            return Response({'detail': 'Payment initialization failed'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'authorization_url': data['data']['authorization_url'],  # redirect user here
            'access_code': data['data']['access_code'],
            'reference': data['data']['reference'],
            'public_key': settings.PAYSTACK_PUBLIC_KEY
        })


class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference):
        response = requests.get(
            f'{PAYSTACK_BASE_URL}/transaction/verify/{reference}',
            headers=paystack_headers()
        )

        data = response.json()

        if not data.get('status'):
            return Response({'detail': 'Verification failed'}, status=status.HTTP_400_BAD_REQUEST)

        transaction = data['data']

        if transaction['status'] == 'success':
            order_id = transaction['metadata'].get('order_id')
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                if order.status == 'pending':
                    order.status = 'confirmed'
                    order.save()
            except Order.DoesNotExist:
                pass

            return Response({'detail': 'Payment successful', 'status': 'success'})

        return Response({'detail': 'Payment not successful', 'status': transaction['status']})


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # verify webhook signature
        paystack_signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
        computed = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            request.body,
            hashlib.sha512
        ).hexdigest()

        if paystack_signature != computed:
            return Response({'detail': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        payload = json.loads(request.body)
        event = payload.get('event')

        if event == 'charge.success':
            order_id = payload['data']['metadata'].get('order_id')
            try:
                order = Order.objects.get(id=order_id)
                if order.status == 'pending':
                    order.status = 'confirmed'
                    order.save()
            except Order.DoesNotExist:
                pass

        return Response({'detail': 'Webhook received'}, status=status.HTTP_200_OK)


class PaymentConfigView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'public_key': settings.PAYSTACK_PUBLIC_KEY})