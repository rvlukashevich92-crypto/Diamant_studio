from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            "master",
            "service",
            "appointment_date",
            "appointment_time",
            "gender",
            "comment",
            "client_name",
            "client_phone",
        ]
        