from django.shortcuts import render
from .models import Service


def service_list(request):
    services = Service.objects.all()


    return render(
        request,
            "service.html",
        {
            "services": services
        }
)

