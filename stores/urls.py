from django.urls import path
from .views import (
    RegisterStoreView, StoreDetailView,
    PublicStoreListView, PublicStoreDetailView,
    AdminStoreApprovalView, SellerOrdersView,
    SellerStatsView, SellerProductStatsView
)

urlpatterns = [
    path('', PublicStoreListView.as_view()),
    path('register/', RegisterStoreView.as_view()),
    path('<slug:slug>/', PublicStoreDetailView.as_view()),
    path('manage/<slug:slug>/', StoreDetailView.as_view()),
    path('admin/<uuid:pk>/approval/', AdminStoreApprovalView.as_view()),
    path('dashboard/orders/', SellerOrdersView.as_view()),
    path('dashboard/stats/', SellerStatsView.as_view()),
    path('dashboard/products/', SellerProductStatsView.as_view()),
]