from django.urls import path

from .views import ReporteNominaCSVView


urlpatterns = [
	path("nomina.csv", ReporteNominaCSVView.as_view(), name="reporte-nomina-csv"),
]
