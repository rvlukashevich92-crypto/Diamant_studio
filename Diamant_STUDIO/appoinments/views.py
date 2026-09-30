from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from datetime import datetime, timedelta, date

from rest_framework.viewsets import ModelViewSet

from .models import Application
from .forms import ApplicationForm
from .serializers import AppointmentSerializer
from masters.models import Master
from services.models import Service
from .tasks import send_appointment_notifications_task

import logging

logger = logging.getLogger(__name__)


def get_available_slots(master, service, appointment_date):
    """Генерирует список доступных временных слотов с учетом занятых и выходных дней."""
    if master.days_off.filter(date=appointment_date).exists():
        return []

    slots = []
    current = datetime.combine(appointment_date, master.work_start)
    end = datetime.combine(appointment_date, master.work_end)
    step = timedelta(minutes=service.duration)

    occupied = set(
        Application.objects.filter(
            master=master,
            appointment_date=appointment_date,    
        ).values_list("appointment_time", flat=True)
    )

    while current + step <= end:
        slot_time = current.time()
        
        if appointment_date == date.today() and slot_time <= datetime.now().time():
            current += step
            continue

        if slot_time not in occupied:
            slots.append(slot_time)
        current += step

    return slots


def appointment_create(request):
    """Рендеринг и обработка Django-формы создания записи."""
    if request.method == "POST":
        form = ApplicationForm(request.POST)
        
        with transaction.atomic():
            if form.is_valid():
                appointment = form.save(commit=False)
                if request.user.is_authenticated:
                    appointment.user = request.user
                appointment.save()

                text = (
                    f"🔥 *Новая запись в салон!*\n\n"
                    f"👤 *Клиент:* {appointment.client_name}\n"
                    f"📞 *Телефон:* `{appointment.client_phone}`\n"
                    f"✂️ *Услуга:* {appointment.service.name}\n"
                    f"💇‍♂️ *Мастер:* {appointment.master.name}\n"
                    f"📅 *Дата:* {appointment.appointment_date.strftime('%d.%m.%Y')}\n"
                    f"⏰ *Время:* {appointment.appointment_time.strftime('%H:%M')}\n"
                )
                if appointment.comment:
                    text += f"💬 *Комментарий:* {appointment.comment}"

                # ИСПРАВЛЕНО: Используем apply_async с четким разделением kwargs. 
                # Это 100% убирает ошибку множественных значений аргумента.
                send_appointment_notifications_task.apply_async(
                    kwargs={
                        "text_message": text,
                        "client_name": appointment.client_name,
                        "client_phone": appointment.client_phone,
                        "service_name": appointment.service.name,
                        "date_str": appointment.appointment_date.strftime('%d.%m.%Y'),
                        "time_str": appointment.appointment_time.strftime('%H:%M')
                    }
                )
            
                messages.success(request, "Вы успешно записались! Мы скоро свяжемся с вами.")
                return redirect("index")
            else:
                return render(request, "appointment.html", {"form": form})
    else:
        initial = {}
        service_id = request.GET.get("service_id") or request.GET.get("service")
        master_id = request.GET.get("master_id") or request.GET.get("master")
        
        if service_id:
            initial["service"] = service_id
            if not master_id:
                first_master = Master.objects.filter(services__id=service_id).first()
                if first_master:
                    initial["master"] = first_master.id
                    
        if master_id:
            initial["master"] = master_id

        form = ApplicationForm(initial=initial)

    return render(request, "appointment.html", {"form": form})


def available_slots(request):
    """API эндпоинт для получения свободных слотов времени."""
    master_id = request.GET.get("master")
    service_id = request.GET.get("service")
    appointment_date_str = request.GET.get("date")

    if not (master_id and service_id and appointment_date_str):
        return JsonResponse({"error": "Missing parameters"}, status=400)
    
    try:
        master = Master.objects.get(pk=master_id)
        service = Service.objects.get(pk=service_id)
        appointment_date = date.fromisoformat(appointment_date_str)
    except (Master.DoesNotExist, Service.DoesNotExist, ValueError):
        return JsonResponse({"error": "Invalid master, service or date format"}, status=400)

    slots = get_available_slots(master, service, appointment_date)
    return JsonResponse([slot.strftime("%H:%M") for slot in slots], safe=False)


def master_services(request):
    """API эндпоинт для получения услуг конкретного мастера."""
    master_id = request.GET.get("master")

    if not master_id:
        services = [{"id": s.id, "name": s.name} for s in Service.objects.all()]
        return JsonResponse(services, safe=False)
    
    try:
        master = Master.objects.get(pk=master_id)
    except (Master.DoesNotExist, ValueError):
        return JsonResponse({"error": "Master not found"}, status=400)
    
    services = [{"id": s.id, "name": s.name} for s in master.services.all()]
    return JsonResponse(services, safe=False)


class AppointmentViewSet(ModelViewSet):
    """REST API Эндпоинт для записи (DRF)."""
    queryset = Application.objects.select_related('master', 'service').all()
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            appointment = serializer.save()

        # ИСПРАВЛЕНО: Используем аналогичный безопасный apply_async для DRF
        text = (
            f"🔥 *Новая запись через API!*\n\n"
            f"👤 *Клиент:* {appointment.client_name}\n"
            f"📞 *Телефон:* `{appointment.client_phone}`\n"
            f"✂️ *Услуга:* {appointment.service.name}\n"
            f"💇‍♂️ *Мастер:* {appointment.master.name}\n"
            f"📅 *Дата:* {appointment.appointment_date.strftime('%d.%m.%Y')}\n"
            f"⏰ *Время:* {appointment.appointment_time.strftime('%H:%M')}\n"
        )
        send_appointment_notifications_task.apply_async(
            kwargs={
                "text_message": text,
                "client_name": appointment.client_name,
                "client_phone": appointment.client_phone,
                "service_name": appointment.service.name,
                "date_str": appointment.appointment_date.strftime('%d.%m.%Y'),
                "time_str": appointment.appointment_time.strftime('%H:%M')
            }
        )