from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

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
		if request.user.rol == "gerente_sucursal" and detalle.nomina.sucursal_id != request.user.sucursal_id:
			return self.permission_denied(request)
		return generar_comprobante_pdf(detalle)
