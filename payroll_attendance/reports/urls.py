from django.urls import path

from .views import ReporteNominaCSVView


urlpatterns = [
	path("payroll.csv", ReporteNominaCSVView.as_view(), name="reporte-payroll-csv"),
]
