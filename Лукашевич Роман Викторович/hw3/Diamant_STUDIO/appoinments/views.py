from django.shortcuts import render, redirect
from .models import Application
from .forms import ApplicationForm
from django.contrib import messages
from datetime import datetime, timedelta
from django.http import JsonResponse
from masters.models import Master
from services.models import Service
from datetime import date



def get_available_slots(master, service, appointment_date):
    slots = []

    current = datetime.combine(
        appointment_date,
        master.work_start
    )

    end = datetime.combine(
        appointment_date,
        master.work_end
        )
    
    step = timedelta(minutes=service.duration)

    occupied = set(
        Application.objects.filter(
            master=master,
            appointment_date=appointment_date,    
        ).values_list(
            "appointment_time",
            flat=True,
        )
    )

    while current + step <= end:
        slots.append(current.time())
        current += step

    return slots


def appointment_create(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            if request.user.is_authenticated:
                appointment.user = request.user

            appointment.save()
        
            messages.success(request, "Вы успешно записались! Мы скоро свяжемся с вами.")
            return redirect("index")
    else:
        initial = {}
        # Читаем параметры, которые пришли с главной страницы
        service_id = request.GET.get("service_id") or request.GET.get("service")
        master_id = request.GET.get("master_id") or request.GET.get("master")
        
        if service_id:
            initial["service"] = service_id
            # Если мастер не выбран, автоматически выберем первого мастера для этой услуги
            if not master_id:
                first_master = Master.objects.filter(services__id=service_id).first()
                if first_master:
                    initial["master"] = first_master.id
                    
        if master_id:
            initial["master"] = master_id

        form = ApplicationForm(initial=initial)

    return render(request, "appointment.html", {"form": form})



def available_slots(request):

    master_id = request.GET.get("master")
    service_id = request.GET.get("service")
    appointment_date = request.GET.get("date")

    if not (
        master_id and service_id and appointment_date
    ):
        return JsonResponse([], safe=False)
    
    

    master = Master.objects.get(pk=master_id)
    service = Service.objects.get(pk=service_id)
    appointment_date = date.fromisoformat(appointment_date)

    slots = get_available_slots(
        master,
        service,
        appointment_date,
    )

    return JsonResponse(
        [
            slot.strftime("%H:%M")
            for slot in slots
        ],
        safe=False
    )



from services.models import Service  # Убедитесь, что импорт есть вверху файла

def master_services(request):
    master_id = request.GET.get("master")

    # ЕСЛИ МАСТЕР НЕ ВЫБРАН: отдаем абсолютно все услуги салона
    if not master_id or master_id == "":
        services = [
            {
                "id": service.id, 
                "name": service.name,
            }
            for service in Service.objects.all()
        ]
        return JsonResponse(services, safe=False)
    
    # ЕСЛИ МАСТЕР ВЫБРАН: отдаем только его услуги (ваш оригинальный код)
    try:
        master = Master.objects.get(pk=master_id)
    except Master.DoesNotExist:
        return JsonResponse([], safe=False)
    
    services = [
        {
            "id": service.id, 
            "name": service.name,
        }
        for service in master.services.all()
    ]

    return JsonResponse(services, safe=False)

