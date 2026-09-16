"""URLs del proyecto."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("usuarios.urls_auth")),
    path("api/usuarios/", include("usuarios.urls")),
    path("api/sucursales/", include("sucursales.urls")),
    path("api/registro/", include("registro.urls")),
    path("api/asistencia/", include("registro.urls")),
    path("api/nomina/", include("nomina.urls")),
    path("api/reglas-laborales/", include("reglas_laborales.urls")),
    path("api/novedades/", include("novedades.urls")),
    path("api/privacidad/", include("privacidad.urls")),
    path("api/comprobantes/", include("comprobantes.urls")),
    path("api/solicitudes/", include("solicitudes.urls")),
    path("api/reportes/", include("reportes.urls")),
]
