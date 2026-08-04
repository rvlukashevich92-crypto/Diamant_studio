import os
import telebot

token = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        
        menu_button = bot.get_chat_menu_button(message.chat.id)
        
       
        if menu_button and menu_button.type == "web_app":
            web_app_url = menu_button.web_app.url
        else:
            # Запасной вариант на случай, если Telegram долго отвечает
            web_app_url = "https://shaggy-badgers-post.loca.lt/appointment/"
    except Exception:
        web_app_url = "https://shaggy-badgers-post.loca.lt/appointment/"

    keyboard = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(
        text="💅 Выбрать мастера и время",
        web_app=telebot.types.WebAppInfo(url=web_app_url)
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
    bot.infinity_polling(timeout=10, long_polling_timeout=5)