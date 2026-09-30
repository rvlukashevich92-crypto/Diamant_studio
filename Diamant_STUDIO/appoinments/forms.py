import re
from django import forms
from .models import Application
from django.utils import timezone
from datetime import datetime, time, timedelta



class ApplicationForm(forms.ModelForm):
    appointment_time = forms.TimeField(
                    input_formats=['%H:%M'],
                    widget=forms.Select(attrs={"class": "form-control", "id": "appointment_time",})
                    )   
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
                    }
            ),

            "service": forms.Select(
                attrs={"class": "form-select",
                       "id":"service",
                       }
            ),

            "appointment_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "id": "appointment_date",
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
        service = cleaned_data.get("service")
        appointment_date = cleaned_data.get("appointment_date")
        appointment_time = cleaned_data.get("appointment_time")

        # 1. Жесткая проверка: если чего-то нет — сразу прерываемся
        if not master or not service or not appointment_date or not appointment_time:
            raise forms.ValidationError("Необходимо заполнить все обязательные поля для записи.")

        # 2. Базовая проверка на прошедшее время
        selected = datetime.combine(appointment_date, appointment_time)
        if timezone.is_naive(selected):
            selected = timezone.make_aware(selected)

        if selected < timezone.now():
            raise forms.ValidationError("Нельзя записаться на прошедшее время.")

        # 3. Вычисляем интервалы (теперь мы на 100% уверены, что все переменные существуют)
        new_start = datetime.combine(appointment_date, appointment_time)
        new_end = new_start + timedelta(minutes=service.duration)
        closing_time = time(20, 0)

        # 4. Проверка на время закрытия салона
        if new_end.time() > closing_time or new_end.date() > appointment_date:
            raise forms.ValidationError(
                f"Выбранная услуга длится {service.duration} мин. "
                f"Мастер закончит работу в {new_end.strftime('%H:%M')}, но салон закрывается в {closing_time.strftime('%H:%M')}."
            )

        # 5. ПРОДВИНУТАЯ ВАЛИДАЦИЯ: Проверка пересечения интервалов записей (Овербукинг)
        existing_appointments = Application.objects.select_for_update().filter(
            master=master,
            appointment_date=appointment_date
        ).select_related('service')

        # Исключаем текущую запись при редактировании (переносе времени)
        if self.instance and self.instance.pk:
            existing_appointments = existing_appointments.exclude(pk=self.instance.pk)

        for app in existing_appointments:
            current_start = datetime.combine(app.appointment_date, app.appointment_time)
            current_end = current_start + timedelta(minutes=app.service.duration)

            if new_start < current_end and new_end > current_start:
                formatted_start = app.appointment_time.strftime('%H:%M')
                formatted_end = current_end.strftime('%H:%M')
                
                raise forms.ValidationError(
                    f"Внимание: Мастер {master.name} в это время занят. "
                    f"Слот с {formatted_start} по {formatted_end} забронирован под услугу '{app.service.name}'."
                )

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ограничение минимальной даты для выбора в календаре
        self.fields["appointment_date"].widget.attrs["min"] = (
            timezone.localdate().isoformat()
        )

        # Проверяем мастера в отправленных данных (POST) или в начальных данных (GET/initial)
        master_id = self.data.get("master") or self.initial.get("master")

        if master_id:
            from masters.models import Master
            try:
                master = Master.objects.get(pk=master_id)
                self.fields["service"].queryset = master.services.all()
            except Master.DoesNotExist:
                from services.models import Service
                self.fields["service"].queryset = Service.objects.all()
        else:
           
            # чтобы пользователь мог выбрать услугу до выбора мастера
            from services.models import Service
            self.fields["service"].queryset = Service.objects.all()

    def clean_client_phone(self):
        client_phone = self.cleaned_data.get("client_phone")
        clean_phone = re.sub(r'[\s\-\(\)]', '', client_phone)
        phone_regex = r'^(?:\+375|375|80)(?:25|29|33|44|15)\d{7}$'
    
        if not re.match(phone_regex, clean_phone):
            raise forms.ValidationError("Неверный формат номера телефона Республики Беларусь.")
        
        if clean_phone.startswith('80'):
            clean_phone = '+375' + clean_phone[2:]
        elif not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        return clean_phone