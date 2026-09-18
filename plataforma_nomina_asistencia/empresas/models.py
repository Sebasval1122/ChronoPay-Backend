from django.db import models


class Empresa(models.Model):
    nombre = models.CharField(max_length=150)
    nit_o_identificacion = models.CharField(max_length=50, blank=True)
    email_contacto = models.EmailField()
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
