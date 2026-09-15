from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.TextChoices):
    ADMIN_GENERAL = "admin_general", "Admin general"
    GERENTE_SUCURSAL = "gerente_sucursal", "Gerente de sucursal"
    EMPLEADO = "empleado", "Empleado"


class Usuario(AbstractUser):
    """
    Usuario del sistema. Reemplaza el modelo de usuario por defecto de
    Django para poder agregar rol, sucursal y salario.
    """

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.EMPLEADO,
    )

    # Un admin_general no pertenece a una sucursal específica.
    # Un gerente_sucursal o empleado sí.
    sucursal = models.ForeignKey(
        "sucursales.Sucursal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
    )

    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    salario_actual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Salario mensual base actual del empleado"
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

    @property
    def es_admin_general(self):
        return self.rol == Rol.ADMIN_GENERAL

    @property
    def es_gerente_sucursal(self):
        return self.rol == Rol.GERENTE_SUCURSAL

    @property
    def es_empleado(self):
        return self.rol == Rol.EMPLEADO


class HistorialSalarial(models.Model):
    """
    Registra cada cambio de salario de un usuario, para trazabilidad
    y auditoría (uno de los diferenciadores del proyecto).
    """

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="historial_salarial"
    )
    salario_anterior = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salario_nuevo = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=255, blank=True)
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cambios_salariales_registrados",
    )

    class Meta:
        verbose_name = "Historial salarial"
        verbose_name_plural = "Historial salarial"
        ordering = ["-fecha_cambio"]

    def __str__(self):
        return f"{self.usuario} : {self.salario_anterior} -> {self.salario_nuevo}"