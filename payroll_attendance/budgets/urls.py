from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BranchBudgetViewSet


router = DefaultRouter()
router.register(r"", BranchBudgetViewSet, basename="branch-budget")

urlpatterns = [
	path("", include(router.urls)),
]