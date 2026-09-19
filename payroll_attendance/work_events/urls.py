from rest_framework.routers import DefaultRouter

from .views import (
	IncapacidadViewSet,
	LicenciaViewSet,
	PermisoViewSet,
)

router = DefaultRouter()
router.register(r"incapacidades", IncapacidadViewSet, basename="incapacidad")
router.register(r"licencias", LicenciaViewSet, basename="licencia")
router.register(r"permisos", PermisoViewSet, basename="permiso")

urlpatterns = router.urls