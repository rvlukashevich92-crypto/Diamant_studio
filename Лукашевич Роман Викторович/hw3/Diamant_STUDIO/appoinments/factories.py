import factory
from masters.models import Master
from services.models import Service
from datetime import time

class MasterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Master

    name = factory.Faker("name")
    work_start = time(9, 0)
    work_end = time(18, 0)
    is_active = True

class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Service

    name = "Маникюр"
    price = 50.00
    duration = 45