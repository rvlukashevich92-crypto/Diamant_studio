import logging
from django.shortcuts import render, get_object_or_404
from .models import Master
from rest_framework.generics import ListAPIView
from .serializers import MasterSerializer
from django.db.models import Avg
from django.utils.decorators import method_decorator 
from django.views.decorators.cache import cache_page

logger = logging.getLogger(__name__)

@cache_page(900)
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
    try:
        master = get_object_or_404(
            Master.objects.prefetch_related("services"),
            pk=pk,
            is_active=True,
        )
        logger.info(f"Просмотр профиля мастера:{master.name} (ID:{pk})")
    except Http404 as e:
        logger.error(f"Ошибка 404! Попытка доступа к несуществующему мастеру с ID:{pk}")
        raise e

    reviews = master.reviews.select_related('user').all()

    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if average_rating: 
        average_rating = round(average_rating, 1)
    else:
        average_rating = "Нет оценок"

    context = {
        'master': master,
        'reviews': reviews,
        'average_rating': average_rating,
    }

    return render(
        request, "masters/master_detail.html", context     
)

class MasterListAPIView(ListAPIView):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer

# Create your views here.
