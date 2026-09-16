from django.db import models


class Nomina(models.Model):
	"""Período de nómina generado para una sucursal."""

	sucursal = models.ForeignKey(
		"sucursales.Sucursal",
		on_delete=models.PROTECT,
		related_name="nominas",
	)
	periodo_inicio = models.DateField()
	periodo_fin = models.DateField()
	estado = models.CharField(max_length=20, default="borrador")
	total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
	creado_en = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Nómina"
		verbose_name_plural = "Nóminas"
		ordering = ["-periodo_fin"]

	def __str__(self):
		return f"Nómina {self.periodo_inicio} - {self.periodo_fin}"


class DetalleNomina(models.Model):
	"""Detalle de pago de un usuario dentro de una nómina."""

	nomina = models.ForeignKey(
		Nomina,
		on_delete=models.CASCADE,
		related_name="detalles",
	)
	usuario = models.ForeignKey(
		"usuarios.Usuario",
		on_delete=models.PROTECT,
		related_name="detalles_nomina",
	)
	salario_base = models.DecimalField(max_digits=14, decimal_places=2, default=0)
	horas_extra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	recargos = models.DecimalField(max_digits=14, decimal_places=2, default=0)
	retencion_fuente = models.DecimalField(max_digits=14, decimal_places=2, default=0)
	novedades = models.DecimalField(max_digits=14, decimal_places=2, default=0)
	total_neto = models.DecimalField(max_digits=14, decimal_places=2, default=0)

	class Meta:
		verbose_name = "Detalle de nómina"
		verbose_name_plural = "Detalles de nómina"
		constraints = [
			models.UniqueConstraint(
				fields=["nomina", "usuario"],
				name="unique_detalle_usuario_por_nomina",
			)
		]
