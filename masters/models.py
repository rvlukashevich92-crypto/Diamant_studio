from django.db import models

class Master(models.Model):

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"
        ordering = ["name"]

    name = models.CharField(max_length=50)
    specialization = models.CharField(max_length=200)
    about = models.TextField()
    photo = models.ImageField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# Create your models here.
