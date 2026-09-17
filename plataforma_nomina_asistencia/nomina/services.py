"""Servicios de cálculo de nómina."""

from decimal import Decimal

from django.db import transaction

from .models import DetalleNomina


def calcular_retencion_fuente(base_gravable):
	"""Calcula una retención conservadora para salarios altos.

	La tarifa exacta debe parametrizarse según UVT y la normativa vigente.
	"""
	base_gravable = Decimal(base_gravable or 0)
	return (base_gravable * Decimal("0.04")).quantize(Decimal("0.01")) if base_gravable > 0 else Decimal("0")


def aplicar_novedades(detalle_nomina, novedades):
	"""Suma novedades monetarias positivas o negativas al detalle."""
	ajuste = sum((Decimal(str(item)) for item in novedades), Decimal("0"))
	detalle_nomina.novedades = ajuste
	detalle_nomina.total_neto = (
		detalle_nomina.salario_base
		+ detalle_nomina.recargos
		+ detalle_nomina.novedades
		- detalle_nomina.retencion_fuente
	)
	return detalle_nomina


@transaction.atomic
def generar_nomina(nomina):
	"""Genera o regenera los detalles de una nómina a partir de empleados activos."""
	nomina.detalles.all().delete()
	empleados = nomina.sucursal.usuarios.filter(is_active=True, activo=True)
	total = Decimal("0")
	for empleado in empleados:
		salario = Decimal(empleado.salario_actual or 0)
		detalle = DetalleNomina.objects.create(
			nomina=nomina,
			usuario=empleado,
			salario_base=salario,
			retencion_fuente=calcular_retencion_fuente(salario),
		)
		detalle.total_neto = detalle.salario_base - detalle.retencion_fuente
		detalle.save(update_fields=["total_neto"])
		total += detalle.total_neto
	nomina.total = total
	nomina.estado = "generada"
	nomina.save(update_fields=["total", "estado"])
	return nomina
