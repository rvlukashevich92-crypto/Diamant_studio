import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


from appoinments.telegram_bot import run_bot

if __name__ == '__main__':
    print("🤖 Скрипт инициализировал Django и вызывает бота...")
    run_bot()
