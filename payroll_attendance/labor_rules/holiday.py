from django.db import models

from .labor_rule import LaborRule


class Holiday(models.Model):
    """Días festivos asociados a una labor_rule laboral por país."""

    labor_rule = models.ForeignKey(
        LaborRule,
        on_delete=models.CASCADE,
        related_name="dias_festivos",
    )
    date = models.DateField()
    description = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Día festivo"
        verbose_name_plural = "Días festivos"
        unique_together = ("labor_rule", "date")
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} - {self.description} ({self.labor_rule.country})"
