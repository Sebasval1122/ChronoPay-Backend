from django.db.models import Q
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import EstadoSolicitud, Solicitud


class SolicitudSerializer(serializers.ModelSerializer):
	solicitante_nombre = serializers.CharField(
		source="solicitante.get_full_name", read_only=True
	)

	class Meta:
		model = Solicitud
		fields = "__all__"
		read_only_fields = [
			"solicitante",
			"estado",
			"revisado_por",
			"comentario_revision",
			"creada_en",
			"actualizada_en",
		]

	def validate(self, attrs):
		if attrs["fecha_fin"] < attrs["fecha_inicio"]:
			raise serializers.ValidationError(
				"La fecha final no puede ser anterior a la fecha inicial."
			)
		return attrs


class SolicitudViewSet(viewsets.ModelViewSet):
	serializer_class = SolicitudSerializer
	permission_classes = [IsAuthenticated]
	queryset = Solicitud.objects.select_related("solicitante", "revisado_por")
	http_method_names = ["get", "post", "patch", "head", "options"]

	def get_queryset(self):
		user = self.request.user
		queryset = super().get_queryset()
		if user.rol == "admin_general":
			return queryset
		if user.rol == "gerente_sucursal":
			return queryset.filter(
				Q(solicitante__sucursal=user.sucursal) | Q(solicitante=user)
			)
		return queryset.filter(solicitante=user)

	def perform_create(self, serializer):
		serializer.save(solicitante=self.request.user)

	@action(detail=True, methods=["post"], url_path="resolver")
	def resolver(self, request, pk=None):
		if request.user.rol not in {"admin_general", "gerente_sucursal"}:
			return Response({"detail": "No tienes permisos para resolver solicitudes."}, status=403)
		solicitud = self.get_object()
		if request.user.rol == "gerente_sucursal" and solicitud.solicitante.sucursal_id != request.user.sucursal_id:
			return Response({"detail": "La solicitud no pertenece a tu sucursal."}, status=403)
		estado = request.data.get("estado")
		if estado not in {EstadoSolicitud.APROBADA, EstadoSolicitud.RECHAZADA}:
			return Response({"detail": "El estado debe ser aprobada o rechazada."}, status=400)
		solicitud.estado = estado
		solicitud.revisado_por = request.user
		solicitud.comentario_revision = request.data.get("comentario_revision", "")
		solicitud.save(update_fields=["estado", "revisado_por", "comentario_revision", "actualizada_en"])
		return Response(self.get_serializer(solicitud).data, status=status.HTTP_200_OK)
