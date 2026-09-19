from django.db import models


class Sucursal(models.Model):
    """Sucursal o punto de venta dentro de la cadena del negocio."""

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sucursales",
    )
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=30, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
