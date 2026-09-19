"""Cálculo de horas ordinarias, extra, daytime_hours/nighttime_hours y dominicales/festivas
a partir de los attendance_records de attendance (``attendance.models.AttendanceRecord``) y la
labor_rule laboral vigente (``labor_rules.models.LaborRule``).

NOTA IMPORTANTE: el reparto de horas extra al final del turno y el divisor
mensual de horas son aproximaciones estándar usadas en nómina en Colombia.
Se recomienda validarlas con un contador o abogado laboralista antes de
usarlas en producción, ya que la ley se está actualizando de forma
progresiva (ver comentarios en ``labor_rules/labor_rule.py``).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone


@dataclass
class HoursBreakdown:
    regular_day_hours: Decimal = Decimal("0")
    regular_night_hours: Decimal = Decimal("0")
    daytime_overtime_hours: Decimal = Decimal("0")
    nighttime_overtime_hours: Decimal = Decimal("0")
    sunday_or_holiday_hours: Decimal = Decimal("0")
    holiday_overtime_hours: Decimal = Decimal("0")

    def sumar(self, otro: "HoursBreakdown") -> None:
        self.regular_day_hours += otro.regular_day_hours
        self.regular_night_hours += otro.regular_night_hours
        self.daytime_overtime_hours += otro.daytime_overtime_hours
        self.nighttime_overtime_hours += otro.nighttime_overtime_hours
        self.sunday_or_holiday_hours += otro.sunday_or_holiday_hours
        self.holiday_overtime_hours += otro.holiday_overtime_hours

    @property
    def total_overtime(self) -> Decimal:
        return (
            self.daytime_overtime_hours
            + self.nighttime_overtime_hours
            + self.holiday_overtime_hours
        )

    @property
    def total_horas(self) -> Decimal:
        return (
            self.regular_day_hours
            + self.regular_night_hours
            + self.daytime_overtime_hours
            + self.nighttime_overtime_hours
            + self.sunday_or_holiday_hours
            + self.holiday_overtime_hours
        )


def obtener_regla_laboral_activa():
    """Devuelve la LaborRule activa a usar en los cálculos.

    Por ahora se asume una sola labor_rule activa (Colombia). Si en el futuro
    se soportan varios países, aquí se debe filtrar por el país de la
    branch del employee.
    """
    from labor_rules.models import LaborRule

    labor_rule = LaborRule.objects.filter(active=True).first()
    if labor_rule is None:
        raise ValueError(
            "No hay una LaborRule activa configurada. "
            "Crea una desde el admin antes de generar nómina."
        )
    return labor_rule


def is_sunday_or_holiday(date, labor_rule) -> bool:
    """True si la date es domingo o está en el calendario de festivos de la labor_rule."""
    if date.weekday() == 6:  # lunes=0 ... domingo=6
        return True
    return labor_rule.dias_festivos.filter(date=date).exists()


def _horas_entre(start: datetime, end: datetime) -> Decimal:
    segundos = max((end - start).total_seconds(), 0)
    return Decimal(segundos) / Decimal(3600)


def _split_day_night(start: datetime, end: datetime, labor_rule) -> tuple[Decimal, Decimal]:
    """Divide el intervalo [start, end) en horas daytime_hours y nighttime_hours,
    según los horarios de la labor_rule laboral, recorriendo día por día
    (necesario porque el horario nocturno cruza la medianoche).
    """
    daytime_hours = Decimal("0")
    nighttime_hours = Decimal("0")
    cursor = start

    while cursor < end:
        day = timezone.localtime(cursor).date()
        inicio_diurno = timezone.make_aware(datetime.combine(day, labor_rule.daytime_start))
        inicio_nocturno = timezone.make_aware(datetime.combine(day, labor_rule.nighttime_start))

        if cursor < inicio_diurno:
            # Aún en el tramo nocturno que viene de la madrugada (antes de las 6 a.m.)
            es_diurno = False
            tramo_fin = inicio_diurno
        elif cursor < inicio_nocturno:
            # Dentro del tramo diurno (ej. 6 a.m. - 7 p.m.)
            es_diurno = True
            tramo_fin = inicio_nocturno
        else:
            # Dentro del tramo nocturno que sigue hasta las 6 a.m. del día siguiente
            es_diurno = False
            tramo_fin = inicio_diurno + timedelta(days=1)

        tramo_fin = min(end, tramo_fin)
        duracion = _horas_entre(cursor, tramo_fin)

        if es_diurno:
            daytime_hours += duracion
        else:
            nighttime_hours += duracion

        cursor = tramo_fin

    return daytime_hours, nighttime_hours


def calculate_attendance_hours(attendance_record, labor_rule) -> HoursBreakdown:
    """Calcula el breakdown de horas de un único attendance_record (una jornada/turno).

    Las horas que exceden ``max_daily_regular_hours`` se toman
    del final del turno como horas extra (el supuesto habitual: el
    employee se queda más tiempo al final de su jornada).
    """
    breakdown = HoursBreakdown()
    if not attendance_record.clock_in_time or not attendance_record.clock_out_time:
        return breakdown  # turno sin cerrar: no se calcula todavía

    clock_in_time = timezone.localtime(attendance_record.clock_in_time)
    clock_out_time = timezone.localtime(attendance_record.clock_out_time)
    if clock_out_time <= clock_in_time:
        return breakdown

    total_horas = _horas_entre(clock_in_time, clock_out_time)
    max_ordinarias = Decimal(labor_rule.max_daily_regular_hours)

    if total_horas > max_ordinarias:
        limite_ordinario = clock_in_time + timedelta(hours=float(max_ordinarias))
    else:
        limite_ordinario = clock_out_time

    es_especial = is_sunday_or_holiday(attendance_record.date, labor_rule)

    # Tramo ordinario
    if limite_ordinario > clock_in_time:
        daytime_hours, nighttime_hours = _split_day_night(clock_in_time, limite_ordinario, labor_rule)
        if es_especial:
            breakdown.sunday_or_holiday_hours += daytime_hours + nighttime_hours
        else:
            breakdown.regular_day_hours += daytime_hours
            breakdown.regular_night_hours += nighttime_hours

    # Tramo extra (lo que exceda la jornada ordinaria)
    if clock_out_time > limite_ordinario:
        daytime_hours, nighttime_hours = _split_day_night(limite_ordinario, clock_out_time, labor_rule)
        if es_especial:
            breakdown.holiday_overtime_hours += daytime_hours + nighttime_hours
        else:
            breakdown.daytime_overtime_hours += daytime_hours
            breakdown.nighttime_overtime_hours += nighttime_hours

    return breakdown


def calculate_period_hours(employee, period_start, period_end, labor_rule) -> HoursBreakdown:
    """Suma el breakdown de horas de todos los attendance_records cerrados del
    employee dentro del período [period_start, period_end]."""
    from attendance.models import AttendanceRecord

    total = HoursBreakdown()
    attendance_records = AttendanceRecord.objects.filter(
        employee=employee,
        fecha__gte=period_start,
        fecha__lte=period_end,
        clock_out_time__isnull=False,
    )
    for attendance_record in attendance_records:
        total.sumar(calculate_attendance_hours(attendance_record, labor_rule))
    return total


def calculate_regular_hour_value(monthly_salary: Decimal, labor_rule) -> Decimal:
    """Valor de la hora ordinaria a partir del salario mensual.

    Se usa el divisor estándar de nómina en Colombia: 30 días al mes,
    repartidos en la jornada diaria ordinaria vigente.
    """
    monthly_hours = Decimal(30) * Decimal(labor_rule.max_daily_regular_hours)
    if monthly_hours == 0:
        return Decimal("0")
    return (Decimal(monthly_salary) / monthly_hours).quantize(Decimal("0.01"))


def calculate_surcharge_value(breakdown: HoursBreakdown, regular_hour_value: Decimal, labor_rule) -> Decimal:
    """Convierte el breakdown de horas en un valor monetario de surcharges,
    aplicando los multiplicadores de ``LaborRule``. Las horas
    ordinarias daytime_hours no generan recargo (van incluidas en el salario
    base), por eso no se suman aquí.
    """
    valor = Decimal("0")
    valor += breakdown.regular_night_hours * regular_hour_value * (labor_rule.nighttime_rate - 1)
    valor += breakdown.daytime_overtime_hours * regular_hour_value * labor_rule.daytime_overtime_rate
    valor += breakdown.nighttime_overtime_hours * regular_hour_value * labor_rule.nighttime_overtime_rate
    valor += breakdown.sunday_or_holiday_hours * regular_hour_value * (labor_rule.sunday_holiday_rate - 1)
    valor += (
        breakdown.holiday_overtime_hours
        * regular_hour_value
        * labor_rule.sunday_holiday_overtime_rate
    )
    return valor.quantize(Decimal("0.01"))