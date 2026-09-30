from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta

from .forms import ClientRegistrationForm
from appoinments.models import Application
from appoinments.forms import ApplicationForm


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile_dashboard')
        messages.error(request, "Неверный логин или пароль.")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='login')
def profile_dashboard(request):
    appointment = request.user.applications.select_related('master', 'service').all().order_by('-appointment_date', '-appointment_time')
    today = timezone.localdate()
    return render(
        request,
        "users/profile.html", 
        {
            "appointments": appointment,
            "today": today
        }
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile_dashboard')

    if request.method == "POST":
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('profile_dashboard')
    else:
        form = ClientRegistrationForm()
        
    return render(request, "users/register.html", {"form": form})


@login_required
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Application, pk=pk, user=request.user)
    
    # Работаем со временем с учетом часовых поясов сервера (Aware datetime)
    now_dt = timezone.localtime(timezone.now())
    appointment_datetime = timezone.make_aware(
        datetime.combine(appointment.appointment_date, appointment.appointment_time)
    )
    
    # Защита: отмена минимум за 2 часа до визита
    if appointment_datetime < now_dt or (appointment_datetime - now_dt) < timedelta(hours=2):
        messages.error(request, "Нельзя отменить запись менее чем за 2 часа до визита. Пожалуйста, свяжитесь с администратором.")
        return redirect('profile_dashboard')
    
    if request.method == "POST":
        appointment.status = 'canceled'  # Мягкое удаление (смена статуса)
        appointment.save()
        messages.success(request, "Запись успешно отменена.")
    return redirect('profile_dashboard')


@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Application, pk=pk, user=request.user)
    
    # Работаем со временем с учетом часовых поясов сервера (Aware datetime)
    now_dt = timezone.localtime(timezone.now())
    appointment_datetime = timezone.make_aware(
        datetime.combine(appointment.appointment_date, appointment.appointment_time)
    )
        
    # Защита: изменение минимум за 2 часа до визита (с корректным текстом ошибки)
    if appointment_datetime < now_dt or (appointment_datetime - now_dt) < timedelta(hours=2):
        messages.error(request, "Нельзя изменить запись менее чем за 2 часа до визита. Пожалуйста, свяжитесь с администратором.")
        return redirect('profile_dashboard')

    if request.method == "POST":
        form = ApplicationForm(request.POST, instance=appointment)
        if form.is_valid():
            # Обертываем сохранение перенесенной записи в транзакцию базы данных
            with transaction.atomic(): 
                form.save()
            messages.success(request, "Запись успешно изменена!")
            return redirect("profile_dashboard")
    else:
        form = ApplicationForm(instance=appointment)

    return render(request, "appointment.html", {"form": form, "is_edit": True})