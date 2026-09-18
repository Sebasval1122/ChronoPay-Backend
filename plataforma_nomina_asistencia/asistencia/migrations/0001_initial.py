from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("registro", "0002_initial"),
        ("sucursales", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    state_operations = [
        migrations.CreateModel(
            name="Marcaje",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField(default=django.utils.timezone.localdate)),
                ("entrada", models.DateTimeField()),
                ("salida", models.DateTimeField(blank=True, null=True)),
                ("motivo_correccion", models.CharField(blank=True, max_length=255)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                ("corregido_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="marcajes_corregidos", to=settings.AUTH_USER_MODEL)),
                ("empleado", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marcajes", to=settings.AUTH_USER_MODEL)),
                ("registrado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="marcajes_registrados", to=settings.AUTH_USER_MODEL)),
                ("sucursal", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="marcajes", to="sucursales.sucursal")),
            ],
            options={
                "ordering": ["-fecha", "-entrada"],
                "db_table": "registro_marcaje",
                "indexes": [
                    models.Index(fields=["empleado", "fecha"], name="asistencia_empleado_fecha_idx"),
                    models.Index(fields=["sucursal", "fecha"], name="asistencia_sucursal_fecha_idx"),
                ],
            },
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations,
            database_operations=[],
        ),
    ]
