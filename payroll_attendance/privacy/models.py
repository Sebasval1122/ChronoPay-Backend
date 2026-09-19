from django.conf import settings
from django.db import models
from django.utils import timezone


class DataPolicy(models.Model):
    """Versión publicada de la política de tratamiento de datos."""

    version = models.CharField(max_length=30, unique=True)
    content = models.TextField()
    vigente = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-id"]

    def __str__(self):
        return f"Política {self.version}"

    def save(self, *args, **kwargs):
        if self.vigente and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class DataConsent(models.Model):
    """Consentimiento otorgado por un user frente a una política."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    policy = models.ForeignKey(DataPolicy, on_delete=models.PROTECT)
    aceptado = models.BooleanField(default=False)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "policy"],
                name="unique_consentimiento_usuario_politica",
            )
        ]
        ordering = ["-granted_at"]