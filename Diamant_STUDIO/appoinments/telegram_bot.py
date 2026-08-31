import os
import telebot
from telebot import apihelper


token = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
   
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = telebot.types.InlineKeyboardButton(
        text="💅 Выбрать мастера и время",
    ) 
    keyboard.add(button)

    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}!\nДобро пожаловать в Diamant Studio.\n"
        f"Нажми на кнопку ниже, чтобы записаться прямо сейчас:",
        reply_markup=keyboard
    )


def run_bot():
    print("🧹 Сбрасываем вебхуки...")
    bot.remove_webhook()
    print("🚀 Запускаем бесконечный опрос Telegram...")
    bot.infinity_polling(timeout=2, long_polling_timeout=1)

user_order = {}

@bot.message_handler(func=lambda message: message.text == "Быстрая запись на процедуру")
def get_client_name(message):
    bot.send_message(message.chat.id, "👤 Введите ваше имя:")
    bot.register_next_step_handler(message, get_client_phone)

def get_client_phone(message):
    user_order['name'] = message.text
    bot.send_message(message.chat.id, "Введите ваш номер телефона (например, +375...):")
    bot.register_next_step_handler(message, save_appointment_to_db)

def save_appointment_to_bd(message):
    user_order['phone'] = message.text

    from appoinments.models import Application

    try:

        new_appointment = Application.objects.create(
            client_name=user_order['name'],
            client_phone=user_order['phone'],
            master_id=1,
            service_id=1,
            appointment_date="2026-08-04",
            appointment_time="12:00"
        )

        bot.send_message(
            message.chat.id,
             f"🎉 Успешно! Роман, вы записаны.\n"
            f"Имя: {user_order['name']}\n"
            f"Телефон: {user_order['phone']}\n"
            f"Запись уже появилась в админке Django!"
        )

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка сосохранения в базу данных: {e}")