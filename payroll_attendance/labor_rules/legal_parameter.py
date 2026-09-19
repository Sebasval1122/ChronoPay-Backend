from django.db import models


class LegalParameter(models.Model):
    """Valores legales variables por país y año."""

    labor_rule = models.ForeignKey(
        "labor_rules.LaborRule",
        on_delete=models.CASCADE,
        related_name="parametros_legales",
    )
    year = models.PositiveIntegerField()
    minimum_wage = models.DecimalField(max_digits=12, decimal_places=2)
    transport_allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        verbose_name = "Parámetro legal"
        verbose_name_plural = "Parámetros legales"
        ordering = ["-year"]
        constraints = [
            models.UniqueConstraint(
                fields=["labor_rule", "year"],
                name="unique_parametro_legal_por_year",
            )
        ]

    def __str__(self):
        return f"{self.labor_rule.country} - {self.year}"