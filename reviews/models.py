from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product
import uuid

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)  # only buyers who ordered can review
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'user')  # one review per product per user
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} — {self.product.name} ({self.rating}/5)"