from rest_framework import serializers
from .models import Store

class StoreSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Store
        fields = (
            'id', 'name', 'slug', 'description',
            'logo', 'status', 'owner_email', 'created_at'
        )
        read_only_fields = ('status', 'slug')

class CreateStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('name', 'description', 'logo')

    def create(self, validated_data):
        from django.utils.text import slugify
        validated_data['slug'] = slugify(validated_data['name'])
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)