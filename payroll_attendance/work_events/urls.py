from rest_framework.routers import DefaultRouter

from .views import (
	SickLeaveViewSet,
	LeaveViewSet,
	PermissionViewSet,
)

router = DefaultRouter()
router.register(r"sickleavees", SickLeaveViewSet, basename="sickleave")
router.register(r"leaves", LeaveViewSet, basename="leave")
router.register(r"permissions", PermissionViewSet, basename="permission")

urlpatterns = router.urls