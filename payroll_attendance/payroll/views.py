from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import is_admin_or_same_branch
from .models import PayrollDetail, Payroll
from .services import generate_payroll
from notifications.models import NotificationType
from notifications.services import notify

class PayrollDetailSerializer(serializers.ModelSerializer):
	user_name = serializers.CharField(source="user.get_full_name", read_only=True)

	class Meta:
		model = PayrollDetail
		fields = "__all__"


class PayrollSerializer(serializers.ModelSerializer):
	detalles = serializers.SerializerMethodField()

	class Meta:
		model = Payroll
		fields = [
			"id", "branch", "period_start", "period_end", "status",
			"total", "created_at", "detalles",
		]
		read_only_fields = ["status", "total", "created_at", "detalles"]

	def validate(self, attrs):
		if attrs["period_end"] < attrs["period_start"]:
			raise serializers.ValidationError("El período final no puede ser anterior al inicial.")
		return attrs

	def get_detalles(self, payroll):
		detalles = payroll.detalles.all()
		request = self.context.get("request")
		if request and request.user.rol == "employee":
			detalles = detalles.filter(user=request.user)
		return PayrollDetailSerializer(detalles, many=True, context=self.context).data


class PayrollViewSet(viewsets.ModelViewSet):
	serializer_class = PayrollSerializer
	permission_classes = [IsAuthenticated]
	queryset = Payroll.objects.select_related("branch").prefetch_related("detalles__user")
	http_method_names = ["get", "post", "patch", "head", "options"]

	def get_queryset(self):
		user = self.request.user
		queryset = super().get_queryset()
		if user.rol == "admin_general":
			return queryset
		return queryset.filter(branch_id=user.branch_id)

	def perform_create(self, serializer):
		if self.request.user.rol not in {"admin_general", "gerente_sucursal"}:
			raise serializers.ValidationError("Solo un administrador o gerente puede crear nóminas.")
		branch = serializer.validated_data["branch"]
		if not is_admin_or_same_branch(self.request.user, branch.pk):
			raise serializers.ValidationError("Solo puedes crear nóminas de tu branch.")
		serializer.save()

	@action(detail=True, methods=["post"], url_path="generar")
	def generar(self, request, pk=None):
		payroll = self.get_object()
		if request.user.rol not in {"admin_general", "gerente_sucursal"}:
			return Response({"detail": "No tienes permissions para generar nóminas."}, status=403)
		generate_payroll(payroll)
		for detalle in payroll.detalles.select_related("user").all():
			notify(
				detalle.user,
				NotificationType.PAYROLL,
				f"Your payroll for {payroll.period_start} to {payroll.period_end} is ready.",
				link="/nomina",
			)
		return Response(self.get_serializer(payroll).data, status=status.HTTP_200_OK)
