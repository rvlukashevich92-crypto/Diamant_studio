import os 
import requests
from celery import shared_task
from django.utils.timezone import now
from .models import Application


@shared_task
def send_appointment_notifications_task(text_message, client_name, client_phone, service_name, date_str, time_str):


    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')

    if token and chat_id:
        url = f"https://telegram.org{token}/sendMessage"
        payload = {
        "chat_id": chat_id,
        "text": text_message,
        "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка фоновой отправки в Telegram через Celery: {e}")

@shared_task
def check_and_send_reminders_task():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')
    
    if token and chat_id:
        return

    current_time = now()
    reminder_target = current_time + timedelta(hours=2)

    upcoming_appointments = Application.objects.filter(
        appointment_date=reminder_target.date(),
        appointment_time__hour=reminder_target.hour,
        appointment_time__minute=reminder_target.minute
    )
    for app in upcoming_appointments:
        reminder_text = (
            f"⏰ **Напоминание о записи в Diamant_studio!**\n\n"
            f"👤 Уважаемый {app.client_name}, ждем Вас через 2 часа!\n"
            f"✂️ Услуга: {app.service.name}\n"
            f"💇‍♂️ Мастер: {app.master.name}\n"
            f"⏰ Время: {app.appointment_time.strftime('%H:%M')}"
        )
        url = f"https://telegram.org{token}/sendMessage"
        payload = {
                "chat_id": chat_id,
                "text": reminder_text,
                "parse_mode": "Markdown"
                }
        try:
            requests.post(url, json=payload, timeout=10)
        except requests.exceptions.RequestException:
            pass

        