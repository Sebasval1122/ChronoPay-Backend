"""Servicios de cálculo de nómina."""

from decimal import Decimal

from django.db import transaction

from .calculo_horas import (
	calcular_horas_periodo,
	calcular_valor_hora_ordinaria,
	calcular_valor_recargos,
	obtener_regla_laboral_activa,
)
from .models import DetalleNomina


def calcular_retencion_fuente(base_gravable):
	"""Calcula una retención conservadora para salarios altos.

	La tarifa exacta debe parametrizarse según UVT y la normativa vigente.
	"""
	base_gravable = Decimal(base_gravable or 0)
	return (base_gravable * Decimal("0.04")).quantize(Decimal("0.01")) if base_gravable > 0 else Decimal("0")


def calcular_ajuste_novedades(empleado, periodo_inicio, periodo_fin):
	"""Calcula el ajuste monetario por incapacidades, licencias y permisos
	del empleado dentro del período. Por ahora las novedades no aprobadas
	no afectan el pago; ajustar aquí cuando se defina la regla de
	descuento/reconocimiento exacta por tipo de novedad.
	"""
	from novedades.models import Incapacidad

	dias_incapacidad = sum(
		(min(inc.fecha_fin, periodo_fin) - max(inc.fecha_inicio, periodo_inicio)).days + 1
		for inc in Incapacidad.objects.filter(
			usuario=empleado,
			aprobada=True,
			fecha_inicio__lte=periodo_fin,
			fecha_fin__gte=periodo_inicio,
		)
	)
	# Placeholder: los primeros 2 días de incapacidad los asume el
	# empleador al 66.67%, el resto la EPS. Ajustar según el caso real.
	if dias_incapacidad:
		return Decimal("0"), dias_incapacidad
	return Decimal("0"), 0


@transaction.atomic
def generar_nomina(nomina):
	"""Genera o regenera los detalles de una nómina, calculando horas
	ordinarias/extra y recargos a partir de los marcajes de asistencia
	de cada empleado en el período de la nómina.
	"""
	regla = obtener_regla_laboral_activa()
	nomina.detalles.all().delete()
	empleados = nomina.sucursal.usuarios.filter(is_active=True, activo=True)
	total = Decimal("0")

	for empleado in empleados:
		salario = Decimal(empleado.salario_actual or 0)

		desglose = calcular_horas_periodo(
			empleado, nomina.periodo_inicio, nomina.periodo_fin, regla
		)
		valor_hora = calcular_valor_hora_ordinaria(salario, regla)
		recargos = calcular_valor_recargos(desglose, valor_hora, regla)

		ajuste_novedades, _ = calcular_ajuste_novedades(
			empleado, nomina.periodo_inicio, nomina.periodo_fin
		)

		detalle = DetalleNomina.objects.create(
			nomina=nomina,
			usuario=empleado,
			salario_base=salario,
			horas_ordinarias_diurnas=desglose.ordinarias_diurnas,
			horas_ordinarias_nocturnas=desglose.ordinarias_nocturnas,
			horas_extra_diurnas=desglose.extra_diurnas,
			horas_extra_nocturnas=desglose.extra_nocturnas,
			horas_dominicales_o_festivas=desglose.dominicales_o_festivas,
			horas_extra_dominicales_o_festivas=desglose.extra_dominicales_o_festivas,
			horas_extra=desglose.total_extra,
			recargos=recargos,
			novedades=ajuste_novedades,
			retencion_fuente=calcular_retencion_fuente(salario + recargos),
		)
		detalle.total_neto = (
			detalle.salario_base
			+ detalle.recargos
			+ detalle.novedades
			- detalle.retencion_fuente
		)
		detalle.save(update_fields=["total_neto"])
		total += detalle.total_neto

	nomina.total = total
	nomina.estado = "generada"
	nomina.save(update_fields=["total", "estado"])
	return nomina