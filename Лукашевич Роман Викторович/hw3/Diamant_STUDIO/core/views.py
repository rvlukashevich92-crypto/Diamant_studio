from django.shortcuts import render
from services.models import Service
from masters.models import Master
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

@cache_page(900)
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
