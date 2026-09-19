"""Servicios de cálculo de nómina."""

from decimal import Decimal

from django.db import transaction

from .hours_calculation import (
	calculate_period_hours,
	calculate_regular_hour_value,
	calculate_surcharge_value,
	obtener_regla_laboral_activa,
)
from .models import PayrollDetail


def calculate_withholding(base_gravable):
	"""Calcula una retención conservadora para salarios altos.

	La tarifa exacta debe parametrizarse según UVT y la normativa vigente.
	"""
	base_gravable = Decimal(base_gravable or 0)
	return (base_gravable * Decimal("0.04")).quantize(Decimal("0.01")) if base_gravable > 0 else Decimal("0")


def calculate_work_event_adjustment(employee, period_start, period_end):
	"""Calcula el ajuste monetario por sickleavees, leaves y permissions
	del employee dentro del período. Por ahora las work_events no aprobadas
	no afectan el pago; ajustar aquí cuando se defina la labor_rule de
	descuento/reconocimiento exacta por type de novedad.
	"""
	from work_events.models import SickLeave

	dias_sickleave = sum(
		(min(inc.end_date, period_end) - max(inc.start_date, period_start)).days + 1
		for inc in SickLeave.objects.filter(
			user=employee,
			approved=True,
			start_date__lte=period_end,
			end_date__gte=period_start,
		)
	)
	# Placeholder: los primeros 2 días de sickleave los asume el
	# empleador al 66.67%, el resto la EPS. Ajustar según el caso real.
	if dias_sickleave:
		return Decimal("0"), dias_sickleave
	return Decimal("0"), 0


@transaction.atomic
def generate_payroll(payroll):
	"""Genera o regenera los detalles de una nómina, calculando horas
	ordinarias/extra y surcharges a partir de los attendance_records de attendance
	de cada employee en el período de la nómina.
	"""
	labor_rule = obtener_regla_laboral_activa()
	payroll.detalles.all().delete()
	empleados = payroll.branch.users.filter(is_active=True, active=True)
	total = Decimal("0")

	for employee in empleados:
		salario = Decimal(employee.current_salary or 0)

		breakdown = calculate_period_hours(
			employee, payroll.period_start, payroll.period_end, labor_rule
		)
		valor_hora = calculate_regular_hour_value(salario, labor_rule)
		surcharges = calculate_surcharge_value(breakdown, valor_hora, labor_rule)

		ajuste_novedades, _ = calculate_work_event_adjustment(
			employee, payroll.period_start, payroll.period_end
		)

		detalle = PayrollDetail.objects.create(
			payroll=payroll,
			user=employee,
			base_salary=salario,
			regular_day_hours=breakdown.regular_day_hours,
			regular_night_hours=breakdown.regular_night_hours,
			overtime_day_hours=breakdown.daytime_overtime_hours,
			overtime_night_hours=breakdown.nighttime_overtime_hours,
			sunday_or_holiday_hours=breakdown.sunday_or_holiday_hours,
			holiday_overtime_hours=breakdown.holiday_overtime_hours,
			overtime_hours=breakdown.total_overtime,
			surcharges=surcharges,
			work_events=ajuste_novedades,
			withholding=calculate_withholding(salario + surcharges),
		)
		detalle.net_total = (
			detalle.base_salary
			+ detalle.surcharges
			+ detalle.work_events
			- detalle.withholding
		)
		detalle.save(update_fields=["net_total"])
		total += detalle.net_total

	payroll.total = total
	payroll.status = "generada"
	payroll.save(update_fields=["total", "status"])
	return payroll