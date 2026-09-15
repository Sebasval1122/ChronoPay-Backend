# Base de datos

Esta carpeta centraliza la configuración de conexión a la base de datos.

## Uso recomendado

- Desarrollo local: SQLite
- Producción o integración: PostgreSQL
- Cambios de entorno: definir variables en .env

Ejemplo de variables:

DB_ENGINE=django.db.backends.postgresql
DB_NAME=chronopay_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

Para enlazar luego:

- actualizar config/settings.py
- usar DATABASES = {"default": {...}}
- correr migraciones con python manage.py migrate
