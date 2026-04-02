from django.urls import path
from .views import InitializePaymentView, VerifyPaymentView, PaystackWebhookView, PaymentConfigView

urlpatterns = [
    path('config/', PaymentConfigView.as_view()),
    path('initialize/', InitializePaymentView.as_view()),
    path('verify/<str:reference>/', VerifyPaymentView.as_view()),
    path('webhook/', PaystackWebhookView.as_view()),
]