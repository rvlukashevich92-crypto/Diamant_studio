from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    """Сериализатор модели услуг"""
    class Meta:
        model = Service
        fields = '__all__'