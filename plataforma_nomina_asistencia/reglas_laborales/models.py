from django.db import models


class ReglaLaboral(models.Model):
    """
    Define cómo se calculan las horas extra, recargos y prestaciones
    para un país. Los valores por defecto corresponden a Colombia
    (Código Sustantivo del Trabajo, Ley 2101 de 2021 y Ley 2466 de 2025).

    IMPORTANTE: la Ley 2466 de 2025 aumenta el recargo dominical/festivo
    de forma progresiva (80% -> 90% -> 100% entre 2025 y 2027), y la
    jornada semanal máxima se redujo de 48 a 42 horas de forma gradual
    hasta julio de 2026. Verifica y actualiza estos valores desde el
    panel de admin cuando cambie la normativa.
    """

    pais = models.CharField(max_length=100, unique=True, default="Colombia")

    # Horario diurno/nocturno. En Colombia el horario nocturno inicia
    # a las 7:00 p.m. (19:00) desde la Ley 2466 de 2025.
    hora_inicio_diurno = models.TimeField(default="06:00")
    hora_inicio_nocturno = models.TimeField(default="19:00")

    # Multiplicadores sobre la hora ordinaria (1.25 = 25% de recargo)
    # Valores vigentes en Colombia a partir del 1 de julio de 2026:
    recargo_hora_extra_diurna = models.DecimalField(
        max_digits=4, decimal_places=2, default=1.25,
        help_text="Hora extra diurna: 25% de recargo"
    )
    recargo_hora_extra_nocturna = models.DecimalField(
        max_digits=4, decimal_places=2, default=1.75,
        help_text="Hora extra nocturna: 75% de recargo"
    )
    recargo_nocturno = models.DecimalField(
        max_digits=4, decimal_places=2, default=1.35,
        help_text="Trabajo ordinario nocturno: 35% de recargo"
    )
    recargo_dominical_o_festivo = models.DecimalField(
        max_digits=4, decimal_places=2, default=1.90,
        help_text=(
            "Trabajo ordinario dominical o festivo: 90% de recargo "
            "(vigente del 1 jul 2026 al 30 jun 2027; sube a 100% después)"
        )
    )
    recargo_nocturno_dominical_o_festivo = models.DecimalField(
        max_digits=4, decimal_places=2, default=2.25,
        help_text="Trabajo ordinario nocturno en dominical/festivo: 125% de recargo"
    )
    recargo_hora_extra_dominical_o_festivo = models.DecimalField(
        max_digits=4, decimal_places=2, default=2.15,
        help_text="Hora extra diurna en dominical/festivo: 115% de recargo"
    )
    recargo_hora_extra_nocturna_dominical_o_festivo = models.DecimalField(
        max_digits=4, decimal_places=2, default=2.65,
        help_text="Hora extra nocturna en dominical/festivo: 165% de recargo"
    )

    # Límites legales (Ley 2101 de 2021: jornada de 42 horas semanales
    # desde el 15 de julio de 2026)
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


class DiaFestivo(models.Model):
    """
    Días festivos por país (en Colombia, los definidos por la Ley 51 de
    1983 y los que se rigen por la Ley Emiliani). Se usan para aplicar
    el recargo dominical/festivo al calcular la nómina.
    """

    regla_laboral = models.ForeignKey(
        ReglaLaboral, on_delete=models.CASCADE, related_name="dias_festivos"
    )
    fecha = models.DateField()
    descripcion = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Día festivo"
        verbose_name_plural = "Días festivos"
        unique_together = ("regla_laboral", "fecha")
        ordering = ["fecha"]

    def __str__(self):
        return f"{self.fecha} - {self.descripcion} ({self.regla_laboral.pais})"
