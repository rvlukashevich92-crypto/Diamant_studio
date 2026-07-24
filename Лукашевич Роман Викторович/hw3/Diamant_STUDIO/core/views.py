from django.shortcuts import render
from services.models import Service
from masters.models import Master

def index(request):
    services = Service.objects.all()
    masters = Master.objects.all()

    return render( 
        request,
        "index.html",
        {
            "services": services,
            "masters": masters,
        },
    )

# Create your views here.
