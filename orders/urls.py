from django.urls import path
from .views import CreateOrderView, OrderListView, OrderDetailView, CancelOrderView, AdminOrderUpdateView

urlpatterns = [
    path('', OrderListView.as_view()),
    path('create/', CreateOrderView.as_view()),
    path('<uuid:pk>/', OrderDetailView.as_view()),
    path('<uuid:pk>/cancel/', CancelOrderView.as_view()),
    path('admin/<uuid:pk>/', AdminOrderUpdateView.as_view()),
]