from django.urls import path

from .views import BranchDashboardView


urlpatterns = [
	path("branches/", BranchDashboardView.as_view(), name="branch-dashboard"),
]