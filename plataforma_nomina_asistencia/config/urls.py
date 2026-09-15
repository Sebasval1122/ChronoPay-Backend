"""
URLs principales del proyecto: Plataforma de Nómina y Asistencia
Cada app tiene su propio archivo urls.py, incluido aquí bajo su propio prefijo.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Panel de administración de Django
    path("admin/", admin.site.urls),

    # Autenticación (login, refresh token, etc.)
    path("api/auth/", include("usuarios.urls_auth")),

    # Apps del proyecto, cada una expone sus propias rutas
    path("api/usuarios/", include("usuarios.urls")),
    path("api/sucursales/", include("sucursales.urls")),
    path("api/asistencia/", include("asistencia.urls")),
    path("api/nomina/", include("nomina.urls")),
    path("api/reglas-laborales/", include("reglas_laborales.urls")),
    path("api/comprobantes/", include("comprobantes.urls")),
    path("api/solicitudes/", include("solicitudes.urls")),
    path("api/reportes/", include("reportes.urls")),
]
