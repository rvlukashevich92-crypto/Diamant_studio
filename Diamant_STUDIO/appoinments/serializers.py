from rest_framework import serializers
from .models import Application

# Меняем ModelSerializer на HyperlinkedModelSerializer
class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    # Явно указываем ссылки на связанные модели мастеров и услуг
    master = serializers.HyperlinkedRelatedField(
        view_name='api-master-list', # Имя вашего API маршрута для мастеров из urls.py
        read_only=True
    )
    service = serializers.HyperlinkedRelatedField(
        view_name='service-detail',  # Имя вашего API маршрута для услуг из urls.py (по умолчанию 'имямодели-detail')
        read_only=True
    )

    class Meta:
        model = Application
        fields = ['url', 'id', 'master', 'service', 'appointment_date', 'appointment_time', 'client_name', 'client_phone', 'comment']
        extra_kwargs = {
            # 'url' автоматически создаст прямую ссылку на саму эту запись
            'url': {'view_name': 'appointment-detail'}, 
        }