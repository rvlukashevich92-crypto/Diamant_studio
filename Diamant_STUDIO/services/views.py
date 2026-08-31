import logging
from django.shortcuts import render
from .models import Service
from .serializers import ServiceSerializer
from rest_framework.viewsets import ModelViewSet
from django.utils.decorators import method_decorator 
from django.views.decorators.cache import cache_page
from django.core.cache import cache

logger = logging.getLogger(__name__)


@cache_page(900)
def service_list(request):
    logger.info("Клиент запросил HTML-страницу со списком всех услуг.")
    services = Service.objects.all()


    return render(
        request,
        "services/service_list.html",
        {"services": services,}
)

class ServiceViewSet(ModelViewSet):
    """Универсальный контроллер для полного управления услугами (CRUD)"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def list(self, request, *args, **kwargs):
        cached_services = cache.get('api_services_json_list')

        if cached_services is None:
            logger.warning("Кэш Redis пуст! Запрос списка услуг направлен напрямую в PostgreSQL")
            response = super().list(request, *args, **kwargs)
            cache.set('api_services_json_list', response.data, 900)
            return response

        
        logger.info("Успешно! Список услуг выдан из оперативной памяти Redis.")
        from rest_framework.response import Response
        return Response(cached_services)

