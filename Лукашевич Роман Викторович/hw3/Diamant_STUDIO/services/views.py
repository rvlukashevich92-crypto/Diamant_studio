from django.shortcuts import render
from .models import Service
from .serializers import ServiceSerializer
from rest_framework.viewsets import ModelViewSet


def service_list(request):
    services = Service.objects.all()


    return render(
        request,
            "services/service_list.html",
        {
            "services": services,
        }
)

class ServiceViewSet(ModelViewSet):
    """Универсальный контроллер для полного управления услугами (CRUD)"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

