from django import forms
from .models import Application
from django.utils import timezone
from datetime import datetime, time


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            "master",
            "service",
            "appointment_date",
            "appointment_time",
            "gender",
            "client_name",
            "client_phone",
            "comment",
        ]

        widgets = {
            "master": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "master",
                    "placeholder": "Выберите мастера",
                    }
            ),

            "service": forms.Select(
                attrs={"class": "form-select",
                       "id":"service",
                       "placeholder": "Выберите услугу",
                       }
            ),

            "appointment_date": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "id": "appointment_date",
                }
            ),

            "appointment_time": forms.Select(
                attrs={
                    "class": "form-control",
                    "type": "time",
                    "id": "appointment_time",
                }
            ),

            "gender": forms.Select(
                attrs={"class": "form-select",
                       "id": "gender",
                       }
            ),

            "client_name": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "Введите имя",
                       }
            ),

            "client_phone": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "+ 375 (29) 123-45-67",}
            ),

            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Дополнительные пожелания",
                }
            ),
        }

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data["appointment_date"]

        if appointment_date < timezone.localdate():
            raise forms.ValidationError(
                "Нельзя записаться на прошедшую дату."
            )

        return appointment_date

    def clean_appointment_time(self):
        appointment_time = self.cleaned_data["appointment_time"]

        if appointment_time < time(9, 0):
            raise forms.ValidationError(
                "Салон работает с 09:00."
            )

        if appointment_time > time(20, 0):
            raise forms.ValidationError(
                "Салон работает до 20:00."
            )

        return appointment_time

    def clean(self):
        cleaned_data = super().clean()

        master = cleaned_data.get("master")
        appointment_date = cleaned_data.get("appointment_date")
        appointment_time = cleaned_data.get("appointment_time")

        if appointment_date and appointment_time:

            selected = datetime.combine(
                appointment_date,
                appointment_time,
            )

            if timezone.is_naive(selected):
                selected = timezone.make_aware(selected)

            if selected < timezone.now():
                raise forms.ValidationError(
                    "Нельзя записаться на прошедшее время."
                )

        if (
            master
            and appointment_date
            and appointment_time
        ):
            exists = Application.objects.filter(
                master=master,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
            ).exists()

            if exists:
                raise forms.ValidationError(
                    "Это время уже занято."
                )
    
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["appointment_date"].widget.attrs["min"] = (
            timezone.localdate().isoformat()
        )

        master_id = self.data.get("master")

        if master_id:
            from masters.models import Master

            try:
                master = Master.objects.get(pk=master_id)
                self.fields["service"].queryset = master.services.all()
            except Master.DoesNotExist:
                pass
        
        else:
            self.fields["service"].queryset = self.fields["service"].queryset.none()