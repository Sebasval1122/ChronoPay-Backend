from rest_framework.routers import DefaultRouter

from .views import SolicitudViewSet


router = DefaultRouter()
router.register("", SolicitudViewSet, basename="solicitud")
urlpatterns = router.urls
