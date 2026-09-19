from django.db import models


class ReglaLaboral(models.Model):
    """Parámetros legales por país para el cálculo de nómina y horas extra."""

    pais = models.CharField(max_length=100, unique=True, default="Colombia")
    hora_inicio_diurno = models.TimeField(default="06:00")
    hora_inicio_nocturno = models.TimeField(default="19:00")

    recargo_hora_extra_diurna = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.25,
        help_text="Hora extra diurna: 25% de recargo.",
    )
    recargo_hora_extra_nocturna = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.75,
        help_text="Hora extra nocturna: 75% de recargo.",
    )
    recargo_nocturno = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.35,
        help_text="Trabajo ordinario nocturno: 35% de recargo.",
    )
    recargo_dominical_o_festivo = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.90,
        help_text="Trabajo ordinario dominical o festivo: 90% de recargo.",
    )
    recargo_nocturno_dominical_o_festivo = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.25,
        help_text="Trabajo ordinario nocturno en dominical/festivo: 125% de recargo.",
    )
    recargo_hora_extra_dominical_o_festivo = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.15,
        help_text="Hora extra diurna en dominical/festivo: 115% de recargo.",
    )
    recargo_hora_extra_nocturna_dominical_o_festivo = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.65,
        help_text="Hora extra nocturna en dominical/festivo: 165% de recargo.",
    )

    horas_maximas_semanales = models.PositiveIntegerField(default=42)
    horas_maximas_diarias_ordinarias = models.PositiveIntegerField(default=8)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Regla laboral"
        verbose_name_plural = "Reglas laborales"

    def __str__(self):
        return f"Reglas laborales - {self.pais}"
