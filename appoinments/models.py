from django.db import models


class Application(models.Model):
    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ["appointment_date", "appointment_time"]


        constraints = [
            models.UniqueConstraint(
                fields=["master", "appointment_date", "appointment_time"],
                name="unique_master_appointment",
            )
        ]

    class Gender(models.TextChoices):
        MALE = "male", "Мужской"
        FEMALE = "female", "Женский"

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает подтверждения"
        CONFIRMED = "confirmed", "Подтверждена"
        COMPLETED = "completed", "Завершена"
        CANCELED = "canceled", "Отменена"

    user = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="applications", blank=True, null=True,
    )

  
    master = models.ForeignKey(
        "masters.Master", on_delete=models.PROTECT, related_name="applications"
    )

    service = models.ForeignKey(
        "services.Service", on_delete=models.PROTECT, related_name="applications"
    )

  
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    gender = models.CharField(max_length=10, choices=Gender.choices)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    comment = models.TextField(blank=True)
    client_name = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=20)

    def __str__(self):
        return (
            f"{self.user.username} — "
            f"{self.master} — "
            f"{self.service.name} "
            f"({self.appointment_date} {self.appointment_time})"
        )