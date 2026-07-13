from django.shortcuts import render, redirect
from .models import Application
from .forms import ApplicationForm

def appointment_create(request):
    if request.method == "POST":
        form = ApplicationForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect("service_list")
    else:
        form = ApplicationForm()

    return render(request, "appointment.html", {"form": form})
# Create your views here.
