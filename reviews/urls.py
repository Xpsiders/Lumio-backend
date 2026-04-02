from django.urls import path
from .views import ProductReviewsView, ReviewDetailView, UserReviewsView

urlpatterns = [
    path('my-reviews/', UserReviewsView.as_view()),
    path('<slug:slug>/', ProductReviewsView.as_view()),
    path('detail/<uuid:pk>/', ReviewDetailView.as_view()),
]