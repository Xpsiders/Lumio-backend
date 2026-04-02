from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            'id', 'user_email', 'user_name', 'rating',
            'title', 'body', 'is_verified_purchase',
            'created_at', 'updated_at'
        )
        read_only_fields = ('is_verified_purchase',)

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('rating', 'title', 'body')

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5')
        return value