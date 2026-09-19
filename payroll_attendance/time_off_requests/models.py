from django.conf import settings
from django.db import models


class TipoSolicitud(models.TextChoices):
	VACACIONES = "vacaciones", "Vacaciones"
	PERMISO = "permiso", "Permiso"


class EstadoSolicitud(models.TextChoices):
	PENDIENTE = "pendiente", "Pendiente"
	APROBADA = "aprobada", "Aprobada"
	RECHAZADA = "rechazada", "Rechazada"


class Solicitud(models.Model):
	solicitante = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="solicitudes",
	)
	tipo = models.CharField(max_length=20, choices=TipoSolicitud.choices)
	fecha_inicio = models.DateField()
	fecha_fin = models.DateField()
	motivo = models.TextField()
	estado = models.CharField(
		max_length=20,
		choices=EstadoSolicitud.choices,
		default=EstadoSolicitud.PENDIENTE,
	)
	revisado_por = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="solicitudes_revisadas",
	)
	comentario_revision = models.TextField(blank=True)
	creada_en = models.DateTimeField(auto_now_add=True)
	actualizada_en = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-creada_en"]

	def __str__(self):
		return f"{self.get_tipo_display()} - {self.solicitante} ({self.estado})"
# Modelos de solicitudes de vacaciones y permisos
