from rest_framework.routers import DefaultRouter

from .views import SucursalViewSet

router = DefaultRouter()
router.register(r"", SucursalViewSet, basename="sucursal")

urlpatterns = []
urlpatterns += router.urls
