from django.urls import path
from .views import appointment_create, available_slots, master_services

urlpatterns = [
    path("", appointment_create, 
         name="appointment_create"),

    path(
        "available-slots/",
        available_slots,
        name="available_slots"
    ),

    path(
        "master-services/", 
        master_services, 
        name="master-services"),    
]

