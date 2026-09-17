import csv

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from nomina.models import DetalleNomina


class ReporteNominaCSVView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		detalles = DetalleNomina.objects.select_related("usuario", "nomina__sucursal")
		if request.user.rol == "empleado":
			detalles = detalles.filter(usuario=request.user)
		elif request.user.rol == "gerente_sucursal":
			detalles = detalles.filter(nomina__sucursal_id=request.user.sucursal_id)
		response = HttpResponse(content_type="text/csv; charset=utf-8")
		response["Content-Disposition"] = 'attachment; filename="reporte-nomina.csv"'
		writer = csv.writer(response)
		writer.writerow(["Empleado", "Sucursal", "Periodo inicio", "Periodo fin", "Salario base", "Retencion", "Total neto"])
		for detalle in detalles:
			writer.writerow([
				detalle.usuario.get_full_name() or detalle.usuario.username,
				detalle.nomina.sucursal.nombre,
				detalle.nomina.periodo_inicio,
				detalle.nomina.periodo_fin,
				detalle.salario_base,
				detalle.retencion_fuente,
				detalle.total_neto,
			])
		return response
