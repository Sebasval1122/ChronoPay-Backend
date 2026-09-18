from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("registro", "0002_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[migrations.DeleteModel(name="Marcaje")],
            database_operations=[],
        ),
    ]
