from rest_framework import serializers
from .models import Master

class MasterSerializer(serializers.ModelSerializer):
    """Сериализатор для модели мастер"""
    class Meta:
        model = Master
        fields = [
            'id', 
            'name', 
            'specialization', 
            'about', 
            'photo', 
            'is_active', 
            'services', 
            'work_start', 
            'work_end', 
            'experience'
        ]