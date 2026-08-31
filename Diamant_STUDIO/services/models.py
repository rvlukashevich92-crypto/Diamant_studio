from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator



class Service(models.Model):
    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["name"]

    name = models.CharField(max_length=150)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
        )
    duration = models.PositiveIntegerField()

    def __str__(self):
        return self.name

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

@receiver([post_save, post_delete], sender=Service)
def clear_cache_on_service_change(sender, instance, **kwargs):
    """Автоматический сброс кэша Redis при изменении списка услуг"""
    print("🧹 Данные услуг изменились! Автоматически очищаем кэш Redis...")
    cache.clear()