from django.db import models

from .regla_laboral import ReglaLaboral


class DiaFestivo(models.Model):
    """Días festivos asociados a una regla laboral por país."""

    regla_laboral = models.ForeignKey(
        ReglaLaboral,
        on_delete=models.CASCADE,
        related_name="dias_festivos",
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
