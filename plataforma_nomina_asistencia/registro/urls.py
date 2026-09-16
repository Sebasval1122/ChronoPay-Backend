from rest_framework.routers import DefaultRouter

from .views import MarcajeViewSet

router = DefaultRouter()
router.register(r"marcajes", MarcajeViewSet, basename="marcaje")

urlpatterns = router.urls
