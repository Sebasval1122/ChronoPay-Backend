from django.conf import settings
from django.db import models
from django.utils import timezone


class Marcaje(models.Model):
    empleado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="marcajes",
    )
    sucursal = models.ForeignKey(
        "sucursales.Sucursal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marcajes",
    )
    fecha = models.DateField(default=timezone.localdate)
    entrada = models.DateTimeField()
    salida = models.DateTimeField(null=True, blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marcajes_registrados",
    )
    corregido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marcajes_corregidos",
    )
    motivo_correccion = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "-entrada"]
        indexes = [
            models.Index(fields=["empleado", "fecha"]),
            models.Index(fields=["sucursal", "fecha"]),
        ]

    def __str__(self):
        return f"{self.empleado} - {self.fecha}"
