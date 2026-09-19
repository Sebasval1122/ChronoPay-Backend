from rest_framework.routers import DefaultRouter

from .views import ConsentimientoDatosViewSet, PoliticaTratamientoViewSet

router = DefaultRouter()
router.register(r"politicas", PoliticaTratamientoViewSet, basename="policy")
router.register(r"consentimientos", ConsentimientoDatosViewSet, basename="consentimiento")

urlpatterns = router.urls