from django.shortcuts import render

from .models import Master


def master_list(request):
    masters = Master.objects.all()


    return render(
        request,
            "masters.html",
        {
            "masters": masters
        }
)


# Create your views here.
