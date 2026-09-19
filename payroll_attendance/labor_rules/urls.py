from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HolidayViewSet, LaborRuleViewSet

router = DefaultRouter()
router.register(r"reglas", LaborRuleViewSet, basename="reglas-laborales")
router.register(r"dias-festivos", HolidayViewSet, basename="dias-festivos")

urlpatterns = [
    path("", include(router.urls)),
]
