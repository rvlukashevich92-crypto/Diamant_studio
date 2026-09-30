import os 
import requests
import logging
from celery import shared_task
from datetime import timedelta  
from django.utils.timezone import now
from .models import Application

# Настраиваем логгер для этого файла
logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(requests.exceptions.RequestException,),
    retry_backoff=True, # Первая попытка через 2с, потом 4с, 8с...
    max_retries=5       # Максимум 5 попыток, потом падаем окончательно
)
def send_appointment_notifications_task(self, text_message, client_name, client_phone, service_name, date_str, time_str):
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')

    if token and chat_id:
       
        url = f"https://api.telegram.org/bot{token}/sendMessage" 
        payload = {
            "chat_id": chat_id,
            "text": text_message,
            "parse_mode": "Markdown"
        }
        try:
            logger.info("📡 Celery отправляет мгновенное уведомление о записи в Telegram...")
            # ИСПРАВЛЕНО: сохраняем ответ в переменную response
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Уведомление о записи клиента {client_name} успешно доставлено.")
        except requests.exceptions.RequestException as e:
            logger.error(f"🚨 Критический сбой сети Celery при отправке в Telegram: {e}")


@shared_task
def check_and_send_reminders_task():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.warning("⚠️ Проверка напоминаний отменена: отсутствует TELEGRAM_BOT_TOKEN в .env")
        return

    current_time = now()
    reminder_target = current_time + timedelta(hours=2)

    # Ищем записи, до которых осталось ровно 2 часа
    upcoming_appointments = Application.objects.filter(
        appointment_date=reminder_target.date(),
        appointment_time__hour=reminder_target.hour,
        appointment_time__minute=reminder_target.minute
    ).select_related('service', 'master') # select_related ускоряет запросы к связанным моделям
    
    if upcoming_appointments.exists():
        logger.info(f"⏱️ Найдено записей для напоминания за 2 часа: {upcoming_appointments.count()}")

    for app in upcoming_appointments:
        
        # В реальности здесь можно подключить СМС-шлюз (например, sms.by) как альтернативу.
        if not app.client_telegram_chat_id:
            logger.info(f"ℹ️ Пропуск: У клиента {app.client_name} не привязан Telegram.")
            continue

        reminder_text = (
            f"⏰ **Напоминание о записи в Diamant Studio!**\n\n"
            f"👤 Уважаемый(ая) {app.client_name}, ждем Вас через 2 часа!\n"
            f"✂️ Услуга: {app.service.name}\n"
            f"💇‍♂️ Мастер: {app.master.name}\n"
            f"⏰ Время: {app.appointment_time.strftime('%H:%M')}\n\n"
            f"До встречи в салоне! ✨"
        )
       
        
        url = f"https://api.telegram.org/bot{token}/sendMessage" 
        
        payload = {
            "chat_id": app.client_telegram_chat_id, # Отправляем ЛИЧНО клиенту
            "text": reminder_text,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"⏰ Авто-напоминание для {app.client_name} успешно отправлено лично в Telegram.")
        except requests.exceptions.RequestException as e:
            logger.error(f"🚨 Не удалось отправить напоминание для {app.client_name}: {e}")

        