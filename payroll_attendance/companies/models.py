from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=150)
    tax_id_or_identification = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField()
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Empresas"
        ordering = ["name"]

    def __str__(self):
        return self.name
