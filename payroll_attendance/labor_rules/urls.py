from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DiaFestivoViewSet, ReglaLaboralViewSet

router = DefaultRouter()
router.register(r"reglas", ReglaLaboralViewSet, basename="reglas-laborales")
router.register(r"dias-festivos", DiaFestivoViewSet, basename="dias-festivos")

urlpatterns = [
    path("", include(router.urls)),
]
