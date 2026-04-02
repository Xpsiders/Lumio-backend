from django.urls import path
from .views import (
    ProductListView, ProductDetailView,
    CategoryListView, AdminProductCreateView, AdminProductUpdateView, SellerProductListView, 
    SellerProductCreateView, SellerProductUpdateView

)

urlpatterns = [
    path('', ProductListView.as_view()),
    path('categories/', CategoryListView.as_view()),
    path('seller/', SellerProductListView.as_view()),
    path('seller/create/', SellerProductCreateView.as_view()),
    path('seller/<slug:slug>/', SellerProductUpdateView.as_view()),
    path('admin/create/', AdminProductCreateView.as_view()),
    path('admin/<slug:slug>/', AdminProductUpdateView.as_view()),
    path('<slug:slug>/', ProductDetailView.as_view()),
]