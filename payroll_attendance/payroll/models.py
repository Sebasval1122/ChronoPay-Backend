from django.db import models


class Payroll(models.Model):
	"""Período de nómina generado para una branch."""

	branch = models.ForeignKey(
		"branches.Branch",
		on_delete=models.PROTECT,
		related_name="nominas",
	)
	period_start = models.DateField()
	period_end = models.DateField()
	status = models.CharField(max_length=20, default="borrador")
	total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Nómina"
		verbose_name_plural = "Nóminas"
		ordering = ["-period_end"]

	def __str__(self):
		return f"Nómina {self.period_start} - {self.period_end}"


class PayrollDetail(models.Model):
	"""Detalle de pago de un user dentro de una nómina."""

	payroll = models.ForeignKey(
		Payroll,
		on_delete=models.CASCADE,
		related_name="detalles",
	)
	user = models.ForeignKey(
		"users.User",
		on_delete=models.PROTECT,
		related_name="detalles_nomina",
	)
	base_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)

	# Desglose de horas trabajadas en el período, según los attendance_records de attendance
	regular_day_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	regular_night_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	overtime_day_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	overtime_night_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	sunday_or_holiday_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	holiday_overtime_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	overtime_hours = models.DecimalField(
		max_digits=8, decimal_places=2, default=0,
		help_text="Total de horas extra del período (sum de todos los tipos anteriores)"
	)

	surcharges = models.DecimalField(
		max_digits=14, decimal_places=2, default=0,
		help_text="Valor monetario total de surcharges y horas extra sobre el salario base"
	)
	withholding = models.DecimalField(max_digits=14, decimal_places=2, default=0)
	work_events = models.DecimalField(max_digits=14, decimal_places=2, default=0)
	net_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

	class Meta:
		verbose_name = "Detalle de nómina"
		verbose_name_plural = "Detalles de nómina"
		constraints = [
			models.UniqueConstraint(
				fields=["payroll", "user"],
				name="unique_detalle_usuario_por_nomina",
			)
		]