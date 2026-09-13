from django.db import migrations
from datetime import time

def populate_masters(apps, schema_editor):
    # Получаем модели через исторический контекст
    Master = apps.get_model('masters', 'Master')
    Service = apps.get_model('services', 'Service')
    
    # 1. Данные Анастасии
    anastasia, _ = Master.objects.get_or_create(
        name="Анастасия Ковалёва",
        defaults={
            "specialization": "Визажист",
            "about": "Создаю естественные и выразительные образы, подчёркивая индивидуальные черты каждого клиента. Специализируюсь на дневном и вечернем макияже, оформлении бровей и ламинировании ресниц. В работе использую современные техники и профессиональную косметику. Для меня важно, чтобы клиент не только отлично выглядел, но и чувствовал себя уверенно.",
            "experience": 5,
            "work_start": time(8, 0),
            "work_end": time(20, 0),
            "is_active": True
        }
    )
    # Привязываем услуги к Анастасии
    services_anastasia = Service.objects.filter(name__in=["Макияж", "Брови", "Ламинирование ресниц"])
    anastasia.services.add(*services_anastasia)

    # 2. Данные Игоря
    igor, _ = Master.objects.get_or_create(
        name="Игорь Соколов",
        defaults={
            "specialization": "Барбер",
            "about": "Специализируюсь на мужских стрижках, оформлении бороды и создании индивидуального стиля. В работе ценю аккуратность, внимание к деталям и комфорт клиента. Подбираю форму стрижки с учётом особенностей внешности и образа жизни. Постоянно совершенствую техники и слежу за современными тенденциями в барберинге.",
            "experience": 7,
            "work_start": time(9, 0),
            "work_end": time(21, 0),
            "is_active": True
        }
    )
    # Привязываем услуги к Игорю
    services_igor = Service.objects.filter(name__in=["Мужские стрижки", "Оформление бороды", "Стрижка машинкой"])
    igor.services.add(*services_igor)

    # 3. Данные Екатерины
    ekaterina, _ = Master.objects.get_or_create(
        name="Екатерина Иванова",
        defaults={
            "specialization": "Косметолог",
            "about": "Помогаю сохранить здоровье и естественное сияние кожи. Подбираю процедуры индивидуально, учитывая особенности и потребности каждого клиента. Специализируюсь на уходе за лицом, чистке кожи, пилингах и расслабляющих процедурах. В работе использую современные методики и внимательно отношусь к каждому клиенту.",
            "experience": 6,
            "work_start": time(9, 0),
            "work_end": time(20, 0),
            "is_active": True
        }
    )
    # Привязываем услуги к Екатерине
    services_ekaterina = Service.objects.filter(name__in=["Чистка лица", "Уходовые процедуры", "Пилинг", "Массаж лица"])
    ekaterina.services.add(*services_ekaterina)


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0008_alter_master_options_and_more'), # Зависимость от твоей последней рабочей миграции
        ('services', '0002_auto_20260913_1509'),       # Зависимость от созданных ранее услуг
    ]

    operations = [
        migrations.RunPython(populate_masters),
    ]