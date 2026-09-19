from django.db import models


class LaborRule(models.Model):
    """Parámetros legales por país para el cálculo de nómina y horas extra."""

    country = models.CharField(max_length=100, unique=True, default="Colombia")
    daytime_start = models.TimeField(default="06:00")
    nighttime_start = models.TimeField(default="19:00")

    daytime_overtime_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.25,
        help_text="Hora extra diurna: 25% de recargo.",
    )
    nighttime_overtime_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.75,
        help_text="Hora extra nocturna: 75% de recargo.",
    )
    nighttime_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.35,
        help_text="Trabajo ordinario nocturno: 35% de recargo.",
    )
    sunday_holiday_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.90,
        help_text="Trabajo ordinario dominical o festivo: 90% de recargo.",
    )
    sunday_holiday_night_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.25,
        help_text="Trabajo ordinario nocturno en dominical/festivo: 125% de recargo.",
    )
    sunday_holiday_overtime_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.15,
        help_text="Hora extra diurna en dominical/festivo: 115% de recargo.",
    )
    nighttime_overtime_rate_dominical_o_festivo = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.65,
        help_text="Hora extra nocturna en dominical/festivo: 165% de recargo.",
    )

    max_weekly_hours = models.PositiveIntegerField(default=42)
    max_daily_regular_hours = models.PositiveIntegerField(default=8)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Regla laboral"
        verbose_name_plural = "Reglas laborales"

    def __str__(self):
        return f"Reglas laborales - {self.country}"
