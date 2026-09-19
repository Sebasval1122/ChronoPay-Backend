from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.permissions import is_admin_or_same_branch
from payroll.models import PayrollDetail

from .services import generate_pay_slip_pdf


class ComprobanteDetalleView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, detalle_id):
		detalle = get_object_or_404(
			PayrollDetail.objects.select_related("user", "payroll__branch"),
			pk=detalle_id,
		)
		if request.user.rol == "employee" and detalle.user_id != request.user.id:
			return self.permission_denied(request)
		if not is_admin_or_same_branch(request.user, detalle.payroll.branch_id) and request.user.rol != "employee":
			return self.permission_denied(request)
		return generate_pay_slip_pdf(detalle)
