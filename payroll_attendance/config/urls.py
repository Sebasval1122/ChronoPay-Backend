"""URLs del proyecto."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/companies/", include("companies.urls")),
    path("api/auth/", include("users.auth_urls")),
    path("api/users/", include("users.urls")),
    path("api/branches/", include("branches.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/reglas-laborales/", include("labor_rules.urls")),
    path("api/work_events/", include("work_events.urls")),
    path("api/privacy/", include("privacy.urls")),
    path("api/pay_slips/", include("pay_slips.urls")),
    path("api/time_off_requests/", include("time_off_requests.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/budgets/", include("budgets.urls")),
    path("api/dashboard/", include("dashboard.urls")),
]
