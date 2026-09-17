from rest_framework.routers import DefaultRouter

from .views import MarcajeViewSet


router = DefaultRouter()
router.register("marcajes", MarcajeViewSet, basename="asistencia-marcaje")
urlpatterns = router.urls
