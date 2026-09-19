from django.conf import settings
from django.db import models


class WorkEvent(models.Model):
    """Campos comunes de una novedad laboral."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.__class__.__name__} - {self.user}"


class SickLeave(WorkEvent):
    """SickLeave médica reportada por un user."""

    diagnosis = models.CharField(max_length=255, blank=True)


class Leave(WorkEvent):
    """Leave laboral approved para un user."""

    reason = models.CharField(max_length=255)


class Permission(WorkEvent):
    """Permission laboral solicitado por un user."""

    reason = models.CharField(max_length=255)
