from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    PAYROLL = "payroll", "Payroll"
    TIME_OFF = "time_off", "Time off request"
    ATTENDANCE = "attendance", "Attendance"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=100, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.message}"