from rest_framework import serializers
from .models import Master

class MasterSerializer(serializers.ModelSerializer):
    """Сериализатор для модели мастер"""
    class Meta:
        model = Master  
        fields = '__all__'