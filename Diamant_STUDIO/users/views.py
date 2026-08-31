from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
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
    return render(request, "users/login.html", {"form":form})

def logout_view(request):
    logout(request)
    return redirect('index')



@login_required(login_url='login')
def profile_dashboard(request):
    appointment = request.user.applications.all().order_by('-appointment_date', '-appointment_time')

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

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Запись успешно отменена.")

    return redirect('profile_dashboard')

@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Application, pk=pk, user=request.user)

    if request.method == "POST":
        form = ApplicationForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Запись успешно изменена!")
            return redirect("profile_dashboard")
    else:
        form = ApplicationForm(instance=appointment)

    return render(request, "appointment.html", {"form":form, "is_edit": True})



