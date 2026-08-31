#!/bin/sh

# 1. Ждем, пока PostgreSQL полностью подниметься (используем стандартный python-скрипт вместо nc)
echo "⏳ Ожидание запуска базы данных PostgreSQL..."
python -c "
import socket
import time
while True:
    try:
        with socket.create_connection(('db', 5432), timeout=1):
            break
    except OSError:
        time.sleep(1)
"
echo "✅ База данных доступна!"

# 2. Автоматически накатываем миграции
echo "📦 Проверка и применение миграций Django..."
python manage.py migrate --noinput

# 3. Автоматически создаем суперпользователя
echo "👤 Проверка наличия администратора..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', '', 'admin12345')
    print('✅ ' + 'Суперпользователь admin успешно создан!')
else:
    print('ℹ️ ' + 'Администратор уже существует в базе.')
"

# 4. Собираем статику автоматически на новом месте
echo "🎨 Сборка статических файлов..."
python manage.py collectstatic --noinput

# 5. Передаем управление Gunicorn
echo "🚀 Запуск веб-сервера..."
exec "$@"