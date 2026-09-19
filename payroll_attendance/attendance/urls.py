from rest_framework.routers import DefaultRouter

from .views import AttendanceRecordViewSet


router = DefaultRouter()
router.register("marcajes", AttendanceRecordViewSet, basename="attendance-marcaje")
urlpatterns = router.urls