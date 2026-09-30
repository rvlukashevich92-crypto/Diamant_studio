import re
from rest_framework import serializers
from .models import Application
from masters.models import Master
from services.models import Service

class AppointmentSerializer(serializers.ModelSerializer):
    
    # Фронтенду/боту НАМНОГО проще прислать числовой ID, чем собирать URL-ссылку.
    # queryset обязателен, иначе DRF не сможет проверить, существуют ли такие мастер и услуга.
    master_id = serializers.PrimaryKeyRelatedField(
        queryset=Master.objects.all(),
        source='master', # Связывает входящий id с полем 'master' в модели Application
        write_only=True  # Поле нужно только при отправке данных (POST/PUT)
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service', # Связывает входящий id с полем 'service' в модели Application
        write_only=True
    )

    # Эти поля отдадут фронтенду красивые ссылки в ответе (GET), реализуя HATEOAS REST стандарт
    master = serializers.HyperlinkedRelatedField(
        view_name='master-detail', # Имя роута из urls.py. По дефолту DRF делает: 'имямодели-detail'
        read_only=True
    )
    service = serializers.HyperlinkedRelatedField(
        view_name='service-detail',
        read_only=True
    )

    class Meta:
        model = Application
        # Включаем и ID-поля для записи, и объекты-ссылки для чтения
        fields = [
            'id', 'master_id', 'service_id', 'master', 'service', 
            'appointment_date', 'appointment_time', 
            'client_name', 'client_phone', 'comment'
        ]

    
    # Поскольку студия находится в Гродно, проверяем валидность под белорусские форматы.
    def validate_client_phone(self, value):
        # Очищаем строку от пробелов, скобок и дефисов, чтобы нормализовать ввод
        clean_phone = re.sub(r'[\s\-\(\)]', '', value)

        # Регулярка для РБ: проверяет форматы +375XXXXXXXXX, 375XXXXXXXXX или 80XXXXXXXXX
        phone_regex = r'^(?:\+375|375|80)(?:25|29|33|44|15)\d{7}$'
        
        if not re.match(phone_regex, clean_phone):
            raise serializers.ValidationError(
                "Неверный формат номера телефона. Используйте формат +375 (XX) XXX-XX-XX или 80 (XX) XXX-XX-XX."
            )
        
        
        if clean_phone.startswith('80'):
            clean_phone = '+375' + clean_phone[2:]
        elif not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone

        return clean_phone

    
    # Проверяем базовые вещи ЕЩЕ ДО того, как дергать тяжелые транзакции в базе данных.
    def validate(self, data):
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')

        # 1. Проверка: Дата не должна быть в прошлом
        if appointment_date < serializers.DateTimeField.ZoneInfo().date.today():
            raise serializers.ValidationError({"appointment_date": "Нельзя записаться на прошедшую дату."})

        # 2. Проверка: Если пишемся на сегодня, время не должно быть в прошлом
        from datetime import datetime
        if appointment_date == datetime.now().date() and appointment_time <= datetime.now().time():
            raise serializers.ValidationError({"appointment_time": "Выбранное время на сегодня уже прошло."})

        return data