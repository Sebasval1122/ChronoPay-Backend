from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.permissions import is_admin_or_same_branch
from nomina.models import DetalleNomina

from .services import generar_comprobante_pdf


class ComprobanteDetalleView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, detalle_id):
		detalle = get_object_or_404(
			DetalleNomina.objects.select_related("usuario", "nomina__sucursal"),
			pk=detalle_id,
		)
		if request.user.rol == "empleado" and detalle.usuario_id != request.user.id:
			return self.permission_denied(request)
		if not is_admin_or_same_branch(request.user, detalle.nomina.sucursal_id) and request.user.rol != "empleado":
			return self.permission_denied(request)
		return generar_comprobante_pdf(detalle)
