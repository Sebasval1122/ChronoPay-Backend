from django.db import models


class Branch(models.Model):
    """Branch o punto de venta dentro de la cadena del negocio."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="branches",
    )
    name = models.CharField(max_length=150)
    codigo = models.CharField(max_length=30, unique=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Sucursales"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.codigo})"
