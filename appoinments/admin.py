from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "client_name",
        "client_phone",
        "master",
        "service",
        "appointment_date",
        "appointment_time",
        "status",
    )

    list_filter = (
        "status",
        "master",
        "appointment_date",
    )

    search_fields = (
        "client_name",
        "client_phone",
    )

    ordering = (
        "-appointment_date",
        "-appointment_time",
    )