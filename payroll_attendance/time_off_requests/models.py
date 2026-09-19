from django.conf import settings
from django.db import models


class RequestType(models.TextChoices):
	VACACIONES = "vacaciones", "Vacaciones"
	PERMISO = "permission", "Permission"


class RequestStatus(models.TextChoices):
	PENDIENTE = "pendiente", "Pendiente"
	APROBADA = "approved", "Aprobada"
	RECHAZADA = "rechazada", "Rechazada"


class Request(models.Model):
	requester = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="time_off_requests",
	)
	type = models.CharField(max_length=20, choices=RequestType.choices)
	start_date = models.DateField()
	end_date = models.DateField()
	reason = models.TextField()
	status = models.CharField(
		max_length=20,
		choices=RequestStatus.choices,
		default=RequestStatus.PENDIENTE,
	)
	reviewed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="requests_reviewed",
	)
	review_comment = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.get_type_display()} - {self.requester} ({self.status})"
# Modelos de time_off_requests de vacaciones y permissions
