from django.conf import settings
from django.db import models


class NovedadBase(models.Model):
    """Campos comunes de una novedad laboral."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.TextField(blank=True)
    aprobada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"{self.__class__.__name__} - {self.usuario}"


class Incapacidad(NovedadBase):
    """Incapacidad médica reportada por un usuario."""

    diagnostico = models.CharField(max_length=255, blank=True)


class Licencia(NovedadBase):
    """Licencia laboral aprobada para un usuario."""

    motivo = models.CharField(max_length=255)


class Permiso(NovedadBase):
    """Permiso laboral solicitado por un usuario."""

    motivo = models.CharField(max_length=255)
