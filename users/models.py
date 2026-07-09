from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    telegram_id = models.BigIntegerField(
        unique=True, null=True, blank=True
    )  
    first_name = models.CharField(max_length=100)

   
    username = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.first_name if self.first_name else self.username

