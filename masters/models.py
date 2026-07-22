from django.db import models
import sys
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
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

    services = models.ManyToManyField(
        "services.Service",
        related_name="masters",
        verbose_name="Услуги",
        blank=True,
    )
    work_start = models.TimeField(default="08:00")
    work_end = models.TimeField(default="20:00")
    experience = models.PositiveIntegerField(
        default=1,
        verbose_name="Опыт работы  (лет)"
    )

    def __str__(self):
        return self.name
    
class MasterPortFolioImage(models.Model):
    class Meta:
        verbose_name = "Фотография работы"
        verbose_name_plural = "Галерея работ"

    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="portfolio_images",
        verbose_name="Мастер"
    )
    image = models.ImageField(
        upload_to="masters/portfolio/",
        verbose_name="Фото работы"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата загрузки"
    )

    
    
    def save_image(self, *args, **kwargs):

        if self.image and hasattr(self.image, 'file'):
            img = Image.open(self.image)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            max_size = (1200, 1200)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=80)
            output.seek(0)  

            self.image = InMemoryUploadedFile(
                output, 'ImageField',
                f"{self.image.name.split('.')[0]}.jpg",
                'image/jpeg', sys.getsizeof(output), None
            )      
        super().save_image(*args, **kwargs)

    def __str__(self):
        return f"Фото для мастера {self.master.name} ({self.id})"


# Create your models here.
