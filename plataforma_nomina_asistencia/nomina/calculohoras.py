from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone


@dataclass
class DesgloseHoras:
    ordinarias_diurnas: Decimal = Decimal("0")
    ordinarias_nocturnas: Decimal = Decimal("0")
    extra_diurnas: Decimal = Decimal("0")
    extra_nocturnas: Decimal = Decimal("0")
    dominicales_o_festivas: Decimal = Decimal("0")
    extra_dominicales_o_festivas: Decimal = Decimal("0")

    def sumar(self, otro: "DesgloseHoras") -> None:
        self.ordinarias_diurnas += otro.ordinarias_diurnas
        self.ordinarias_nocturnas += otro.ordinarias_nocturnas
        self.extra_diurnas += otro.extra_diurnas
        self.extra_nocturnas += otro.extra_nocturnas
        self.dominicales_o_festivas += otro.dominicales_o_festivas
        self.extra_dominicales_o_festivas += otro.extra_dominicales_o_festivas

    @property
    def total_extra(self) -> Decimal:
        return (
            self.extra_diurnas
            + self.extra_nocturnas
            + self.extra_dominicales_o_festivas
        )

    @property
    def total_horas(self) -> Decimal:
        return (
            self.ordinarias_diurnas
            + self.ordinarias_nocturnas
            + self.extra_diurnas
            + self.extra_nocturnas
            + self.dominicales_o_festivas
            + self.extra_dominicales_o_festivas
        )


def obtener_regla_laboral_activa():
    """Devuelve la ReglaLaboral activa a usar en los cálculos.

    Por ahora se asume una sola regla activa (Colombia). Si en el futuro
    se soportan varios países, aquí se debe filtrar por el país de la
    sucursal del empleado.
    """
    from reglas_laborales.models import ReglaLaboral

    regla = ReglaLaboral.objects.filter(activo=True).first()
    if regla is None:
        raise ValueError(
            "No hay una ReglaLaboral activa configurada. "
            "Crea una desde el admin antes de generar nómina."
        )
    return regla


def es_dia_festivo_o_dominical(fecha, regla) -> bool:
    """True si la fecha es domingo o está en el calendario de festivos de la regla."""
    if fecha.weekday() == 6:  # lunes=0 ... domingo=6
        return True
    return regla.dias_festivos.filter(fecha=fecha).exists()


def _horas_entre(inicio: datetime, fin: datetime) -> Decimal:
    segundos = max((fin - inicio).total_seconds(), 0)
    return Decimal(segundos) / Decimal(3600)


def _dividir_diurno_nocturno(inicio: datetime, fin: datetime, regla) -> tuple[Decimal, Decimal]:
    """Divide el intervalo [inicio, fin) en horas diurnas y nocturnas,
    según los horarios de la regla laboral, recorriendo día por día
    (necesario porque el horario nocturno cruza la medianoche).
    """
    diurnas = Decimal("0")
    nocturnas = Decimal("0")
    cursor = inicio

    while cursor < fin:
        dia = timezone.localtime(cursor).date()
        inicio_diurno = timezone.make_aware(datetime.combine(dia, regla.hora_inicio_diurno))
        inicio_nocturno = timezone.make_aware(datetime.combine(dia, regla.hora_inicio_nocturno))

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

        tramo_fin = min(fin, tramo_fin)
        duracion = _horas_entre(cursor, tramo_fin)

        if es_diurno:
            diurnas += duracion
        else:
            nocturnas += duracion

        cursor = tramo_fin

    return diurnas, nocturnas


def calcular_horas_marcaje(marcaje, regla) -> DesgloseHoras:
    """Calcula el desglose de horas de un único marcaje (una jornada/turno).

    Las horas que exceden ``horas_maximas_diarias_ordinarias`` se toman
    del final del turno como horas extra (el supuesto habitual: el
    empleado se queda más tiempo al final de su jornada).
    """
    desglose = DesgloseHoras()
    if not marcaje.entrada or not marcaje.salida:
        return desglose  # turno sin cerrar: no se calcula todavía

    entrada = timezone.localtime(marcaje.entrada)
    salida = timezone.localtime(marcaje.salida)
    if salida <= entrada:
        return desglose

    total_horas = _horas_entre(entrada, salida)
    max_ordinarias = Decimal(regla.horas_maximas_diarias_ordinarias)

    if total_horas > max_ordinarias:
        limite_ordinario = entrada + timedelta(hours=float(max_ordinarias))
    else:
        limite_ordinario = salida

    es_especial = es_dia_festivo_o_dominical(marcaje.fecha, regla)

    # Tramo ordinario
    if limite_ordinario > entrada:
        diurnas, nocturnas = _dividir_diurno_nocturno(entrada, limite_ordinario, regla)
        if es_especial:
            desglose.dominicales_o_festivas += diurnas + nocturnas
        else:
            desglose.ordinarias_diurnas += diurnas
            desglose.ordinarias_nocturnas += nocturnas

    # Tramo extra (lo que exceda la jornada ordinaria)
    if salida > limite_ordinario:
        diurnas, nocturnas = _dividir_diurno_nocturno(limite_ordinario, salida, regla)
        if es_especial:
            desglose.extra_dominicales_o_festivas += diurnas + nocturnas
        else:
            desglose.extra_diurnas += diurnas
            desglose.extra_nocturnas += nocturnas

    return desglose


def calcular_horas_periodo(empleado, periodo_inicio, periodo_fin, regla) -> DesgloseHoras:
    """Suma el desglose de horas de todos los marcajes cerrados del
    empleado dentro del período [periodo_inicio, periodo_fin]."""
    from registro.models import Marcaje

    total = DesgloseHoras()
    marcajes = Marcaje.objects.filter(
        empleado=empleado,
        fecha__gte=periodo_inicio,
        fecha__lte=periodo_fin,
        salida__isnull=False,
    )
    for marcaje in marcajes:
        total.sumar(calcular_horas_marcaje(marcaje, regla))
    return total


def calcular_valor_hora_ordinaria(salario_mensual: Decimal, regla) -> Decimal:
    """Valor de la hora ordinaria a partir del salario mensual.

    Se usa el divisor estándar de nómina en Colombia: 30 días al mes,
    repartidos en la jornada diaria ordinaria vigente.
    """
    horas_mensuales = Decimal(30) * Decimal(regla.horas_maximas_diarias_ordinarias)
    if horas_mensuales == 0:
        return Decimal("0")
    return (Decimal(salario_mensual) / horas_mensuales).quantize(Decimal("0.01"))


def calcular_valor_recargos(desglose: DesgloseHoras, valor_hora_ordinaria: Decimal, regla) -> Decimal:
    """Convierte el desglose de horas en un valor monetario de recargos,
    aplicando los multiplicadores de ``ReglaLaboral``. Las horas
    ordinarias diurnas no generan recargo (van incluidas en el salario
    base), por eso no se suman aquí.
    """
    valor = Decimal("0")
    valor += desglose.ordinarias_nocturnas * valor_hora_ordinaria * (regla.recargo_nocturno - 1)
    valor += desglose.extra_diurnas * valor_hora_ordinaria * regla.recargo_hora_extra_diurna
    valor += desglose.extra_nocturnas * valor_hora_ordinaria * regla.recargo_hora_extra_nocturna
    valor += desglose.dominicales_o_festivas * valor_hora_ordinaria * (regla.recargo_dominical_o_festivo - 1)
    valor += (
        desglose.extra_dominicales_o_festivas
        * valor_hora_ordinaria
        * regla.recargo_hora_extra_dominical_o_festivo
    )
    return valor.quantize(Decimal("0.01"))