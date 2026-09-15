"""Configuración base para conexiones de base de datos."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración por defecto para desarrollo local
DEFAULT_DB = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": str(BASE_DIR / "db.sqlite3"),
}

# Plantilla para PostgreSQL en producción o integración
POSTGRES_DB = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "chronopay_db",
    "USER": "postgres",
    "PASSWORD": "postgres",
    "HOST": "localhost",
    "PORT": "5432",
}

# Plantilla para MySQL si luego decides usarlo
MYSQL_DB = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": "chronopay_db",
    "USER": "root",
    "PASSWORD": "",
    "HOST": "localhost",
    "PORT": "3306",
}
