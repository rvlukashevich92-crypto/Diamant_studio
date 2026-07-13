from django.urls import path
from .views import appointment_create

urlpatterns = [
    path("", appointment_create, name="appointment_create"),
]