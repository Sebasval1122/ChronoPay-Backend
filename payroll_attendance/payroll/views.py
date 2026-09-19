from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import is_admin_or_same_branch
from .models import DetalleNomina, Nomina
from .services import generar_nomina


class DetalleNominaSerializer(serializers.ModelSerializer):
	usuario_nombre = serializers.CharField(source="usuario.get_full_name", read_only=True)

	class Meta:
		model = DetalleNomina
		fields = "__all__"


class NominaSerializer(serializers.ModelSerializer):
	detalles = serializers.SerializerMethodField()

	class Meta:
		model = Nomina
		fields = [
			"id", "sucursal", "periodo_inicio", "periodo_fin", "estado",
			"total", "creado_en", "detalles",
		]
		read_only_fields = ["estado", "total", "creado_en", "detalles"]

	def validate(self, attrs):
		if attrs["periodo_fin"] < attrs["periodo_inicio"]:
			raise serializers.ValidationError("El período final no puede ser anterior al inicial.")
		return attrs

	def get_detalles(self, nomina):
		detalles = nomina.detalles.all()
		request = self.context.get("request")
		if request and request.user.rol == "empleado":
			detalles = detalles.filter(usuario=request.user)
		return DetalleNominaSerializer(detalles, many=True, context=self.context).data


class NominaViewSet(viewsets.ModelViewSet):
	serializer_class = NominaSerializer
	permission_classes = [IsAuthenticated]
	queryset = Nomina.objects.select_related("sucursal").prefetch_related("detalles__usuario")
	http_method_names = ["get", "post", "patch", "head", "options"]

	def get_queryset(self):
		user = self.request.user
		queryset = super().get_queryset()
		if user.rol == "admin_general":
			return queryset
		return queryset.filter(sucursal_id=user.sucursal_id)

	def perform_create(self, serializer):
		if self.request.user.rol not in {"admin_general", "gerente_sucursal"}:
			raise serializers.ValidationError("Solo un administrador o gerente puede crear nóminas.")
		sucursal = serializer.validated_data["sucursal"]
		if not is_admin_or_same_branch(self.request.user, sucursal.pk):
			raise serializers.ValidationError("Solo puedes crear nóminas de tu sucursal.")
		serializer.save()

	@action(detail=True, methods=["post"], url_path="generar")
	def generar(self, request, pk=None):
		nomina = self.get_object()
		if request.user.rol not in {"admin_general", "gerente_sucursal"}:
			return Response({"detail": "No tienes permisos para generar nóminas."}, status=403)
		generar_nomina(nomina)
		return Response(self.get_serializer(nomina).data, status=status.HTTP_200_OK)
