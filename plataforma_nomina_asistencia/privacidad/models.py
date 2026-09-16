from django.conf import settings
from django.db import models


class PoliticaTratamiento(models.Model):
    """Versión publicada de la política de tratamiento de datos."""

    version = models.CharField(max_length=30, unique=True)
    contenido = models.TextField()
    vigente = models.BooleanField(default=False)
    publicada_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Política {self.version}"


class ConsentimientoDatos(models.Model):
    """Consentimiento otorgado por un usuario frente a una política."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    politica = models.ForeignKey(PoliticaTratamiento, on_delete=models.PROTECT)
    aceptado = models.BooleanField(default=False)
    otorgado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "politica"],
                name="unique_consentimiento_usuario_politica",
            )
        ]