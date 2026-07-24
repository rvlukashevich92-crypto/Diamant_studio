from django.shortcuts import render, get_object_or_404

from .models import Master


def master_list(request):
    masters = Master.objects.filter(
        is_active=True
    ).prefetch_related("services")


    return render(
        request,
            "masters/master_list.html",
        {
            "masters": masters,
        },
)

def master_detail(request, pk):
    master = get_object_or_404(
        Master.objects.prefetch_related("services"),
        pk=pk,
        is_active=True,
    )

    return render(
        request,
            "masters/master_detail.html",
        {
            "master": master,
        },
)


# Create your views here.
