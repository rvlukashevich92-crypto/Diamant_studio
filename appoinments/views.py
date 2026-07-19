from django.shortcuts import render, redirect
from .models import Application
from .forms import ApplicationForm
from django.contrib import messages
from datetime import datetime, timedelta
from django.http import JsonResponse


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
            form.save()
            messages.success(
                request, 
                "Вы успешно записались! Мы скоро свяжемся с вами."
            )
            return redirect("index")
    else:
        form = ApplicationForm()

    return render(request, "appointment.html", {"form": form})



def available_slots(request):

    master_id = request.GET.get("master")
    service_id = request.GET.get("service")
    appointment_date = request.GET.get("date")

    if not (
        master_id and service_id and appointment_date
    ):
        return JsonResponse([], safe=False)
    
    from masters.models import Master
    from services.models import Service
    from datetime import date

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

from masters.models import Master

def master_services(request):

    master_id = request.GET.get("master")

    if not master_id:
        return JsonResponse([], safe=False)
    
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