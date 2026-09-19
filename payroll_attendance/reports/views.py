import csv

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from payroll.models import PayrollDetail


class ReporteNominaCSVView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		detalles = PayrollDetail.objects.select_related("user", "payroll__branch")
		if request.user.rol == "employee":
			detalles = detalles.filter(user=request.user)
		elif request.user.rol == "gerente_sucursal":
			detalles = detalles.filter(payroll__branch_id=request.user.branch_id)
		response = HttpResponse(content_type="text/csv; charset=utf-8")
		response["Content-Disposition"] = 'attachment; filename="reporte-payroll.csv"'
		writer = csv.writer(response)
		writer.writerow(["Empleado", "Branch", "Periodo start", "Periodo end", "Salario base", "Retencion", "Total neto"])
		for detalle in detalles:
			writer.writerow([
				detalle.user.get_full_name() or detalle.user.username,
				detalle.payroll.branch.name,
				detalle.payroll.period_start,
				detalle.payroll.period_end,
				detalle.base_salary,
				detalle.withholding,
				detalle.net_total,
			])
		return response
