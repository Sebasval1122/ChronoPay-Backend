from django.db.models import Q
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import is_admin_or_same_branch
from .models import RequestStatus, Request
from notifications.models import NotificationType
from notifications.services import notify


class RequestSerializer(serializers.ModelSerializer):
	requester_name = serializers.CharField(
		source="requester.get_full_name", read_only=True
	)

	class Meta:
		model = Request
		fields = "__all__"
		read_only_fields = [
			"requester",
			"status",
			"reviewed_by",
			"review_comment",
			"created_at",
			"updated_at",
		]

	def validate(self, attrs):
		if attrs["end_date"] < attrs["start_date"]:
			raise serializers.ValidationError(
				"La date final no puede ser anterior a la date inicial."
			)
		return attrs


class RequestViewSet(viewsets.ModelViewSet):
	serializer_class = RequestSerializer
	permission_classes = [IsAuthenticated]
	queryset = Request.objects.select_related("requester", "reviewed_by")
	http_method_names = ["get", "post", "patch", "head", "options"]

	def get_queryset(self):
		user = self.request.user
		queryset = super().get_queryset()
		if user.rol == "admin_general":
			return queryset
		if user.rol == "gerente_sucursal":
			return queryset.filter(
				Q(requester__branch=user.branch) | Q(requester=user)
			)
		return queryset.filter(requester=user)

	def perform_create(self, serializer):
		serializer.save(requester=self.request.user)

	@action(detail=True, methods=["post"], url_path="resolve")
	def resolve(self, request, pk=None):
		if request.user.rol not in {"admin_general", "gerente_sucursal"}:
			return Response({"detail": "No tienes permissions para resolve time_off_requests."}, status=403)
		time_off_request = self.get_object()
		if not is_admin_or_same_branch(request.user, time_off_request.requester.branch_id):
			return Response({"detail": "La request no pertenece a tu branch."}, status=403)
		request_status = request.data.get("status")
		if request_status not in {RequestStatus.APROBADA, RequestStatus.RECHAZADA}:
			return Response({"detail": "El status debe ser approved o rechazada."}, status=400)
		time_off_request.status = request_status
		time_off_request.reviewed_by = request.user
		time_off_request.review_comment = request.data.get("review_comment", "")
		time_off_request.save(update_fields=["status", "reviewed_by", "review_comment", "updated_at"])
		notify(
			time_off_request.requester,
			NotificationType.TIME_OFF,
			f"Your {time_off_request.get_type_display().lower()} request was {time_off_request.get_status_display().lower()}.",
			link="/solicitudes",
		)
		return Response(self.get_serializer(time_off_request).data, status=status.HTTP_200_OK)
