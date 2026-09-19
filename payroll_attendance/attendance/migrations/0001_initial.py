from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("branches", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AttendanceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(default=django.utils.timezone.localdate)),
                ("clock_in_time", models.DateTimeField()),
                ("clock_out_time", models.DateTimeField(blank=True, null=True)),
                ("correction_reason", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("corrected_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="marcajes_corregidos", to=settings.AUTH_USER_MODEL)),
                ("employee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marcajes", to=settings.AUTH_USER_MODEL)),
                ("recorded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="marcajes_registrados", to=settings.AUTH_USER_MODEL)),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="marcajes", to="branches.branch")),
            ],
            options={
                "ordering": ["-date", "-clock_in_time"],
                "db_table": "registro_marcaje",
                "indexes": [
                    models.Index(fields=["employee", "date"], name="asistencia_empleado_fecha_idx"),
                    models.Index(fields=["branch", "date"], name="asistencia_sucursal_fecha_idx"),
                ],
            },
        ),
    ]
