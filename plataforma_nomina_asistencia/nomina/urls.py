from rest_framework.routers import DefaultRouter

from .views import NominaViewSet


router = DefaultRouter()
router.register("", NominaViewSet, basename="nomina")
urlpatterns = router.urls
