from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN_GENERAL = "admin_general", "Admin general"
    GERENTE_SUCURSAL = "gerente_sucursal", "Gerente de branch"
    EMPLEADO = "employee", "Empleado"


class User(AbstractUser):
    """
    User del sistema. Reemplaza el modelo de user por defecto de
    Django para poder agregar rol, branch y salario.
    """

    rol = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLEADO,
    )

    # Un admin_general no pertenece a una branch específica.
    # Un gerente_sucursal o employee sí.
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    current_salary = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Salario mensual base actual del employee"
    )

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

    @property
    def is_general_admin(self):
        return self.rol == Role.ADMIN_GENERAL

    @property
    def is_branch_manager(self):
        return self.rol == Role.GERENTE_SUCURSAL

    @property
    def is_employee(self):
        return self.rol == Role.EMPLEADO


class SalaryHistory(models.Model):
    """
    Registra cada cambio de salario de un user, para trazabilidad
    y auditoría (uno de los diferenciadores del proyecto).
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="historial_salarial"
    )
    previous_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_salary = models.DecimalField(max_digits=12, decimal_places=2)
    change_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cambios_salariales_registrados",
    )

    class Meta:
        verbose_name = "Historial salarial"
        verbose_name_plural = "Historial salarial"
        ordering = ["-change_date"]

    def __str__(self):
        return f"{self.user} : {self.previous_salary} -> {self.new_salary}"