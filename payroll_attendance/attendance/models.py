from django.conf import settings
from django.db import models
from django.utils import timezone


class AttendanceRecord(models.Model):
	employee = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="attendance_records",
	)
	branch = models.ForeignKey(
		"branches.Branch",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="attendance_records",
	)
	date = models.DateField(default=timezone.localdate)
	clock_in_time = models.DateTimeField()
	clock_out_time = models.DateTimeField(null=True, blank=True)
	recorded_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="marcajes_registrados",
	)
	corrected_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="marcajes_corregidos",
	)
	correction_reason = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date", "-clock_in_time"]
		db_table = "registro_marcaje"
		indexes = [
			models.Index(
				fields=["employee", "date"],
				name="asistencia_empleado_fecha_idx",
			),
			models.Index(
				fields=["branch", "date"],
				name="asistencia_sucursal_fecha_idx",
			),
		]

	def __str__(self):
		return f"{self.employee} - {self.date}"
