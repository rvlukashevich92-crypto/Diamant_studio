from django.shortcuts import render
from django.core.cache import cache
from services.models import Service
from masters.models import Master

def index(request):
    # КОММЕРЧЕСКИЙ ФИКС: Кэшируем данные из базы, но не саму HTML-страницу
    services = cache.get('homepage_services')
    if not services:
        services = Service.objects.all()
        cache.set('homepage_services', services, 900)

    masters = cache.get('homepage_masters')
    if not masters:
        # Рекомендуется добавить select_related или prefetch_related, если у мастера есть связи
        masters = Master.objects.filter(is_active=True)
        cache.set('homepage_masters', masters, 900)

    return render( 
        request,
        "index.html",
        {
            "services": services,
            "masters": masters,
        },
    )
# Create your views here.
