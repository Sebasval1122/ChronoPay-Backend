from rest_framework.routers import DefaultRouter

from .views import SucursalViewSet

router = DefaultRouter()
router.register(r"", SucursalViewSet, basename="sucursal")

from rest_framework.routers import DefaultRouter

from .views import SucursalViewSet


router = DefaultRouter()
router.register("", SucursalViewSet, basename="sucursal")
urlpatterns = router.urls
urlpatterns += router.urls
