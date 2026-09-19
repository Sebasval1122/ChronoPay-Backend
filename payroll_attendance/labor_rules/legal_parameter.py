from django.db import models


class ParametroLegal(models.Model):
    """Valores legales variables por país y año."""

    regla_laboral = models.ForeignKey(
        "reglas_laborales.ReglaLaboral",
        on_delete=models.CASCADE,
        related_name="parametros_legales",
    )
    anio = models.PositiveIntegerField()
    smmlv = models.DecimalField(max_digits=12, decimal_places=2)
    auxilio_transporte = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        verbose_name = "Parámetro legal"
        verbose_name_plural = "Parámetros legales"
        ordering = ["-anio"]
        constraints = [
            models.UniqueConstraint(
                fields=["regla_laboral", "anio"],
                name="unique_parametro_legal_por_anio",
            )
        ]

    def __str__(self):
        return f"{self.regla_laboral.pais} - {self.anio}"