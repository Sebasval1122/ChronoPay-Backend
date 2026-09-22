from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AttendanceRecord
from .permissions import CanManageAttendance
from .serializers import AttendanceRecordSerializer
from notifications.models import NotificationType
from notifications.services import notify

class AttendanceRecordViewSet(viewsets.ModelViewSet):
	queryset = AttendanceRecord.objects.select_related("employee", "branch")
	serializer_class = AttendanceRecordSerializer
	permission_classes = [CanManageAttendance]
	http_method_names = ["get", "post", "patch", "head", "options"]

	def get_queryset(self):
		user = self.request.user
		queryset = super().get_queryset()
		if user.rol == "admin_general":
			return queryset
		if user.rol == "gerente_sucursal":
			return queryset.filter(branch_id=user.branch_id)
		return queryset.filter(employee=user)

	@action(detail=False, methods=["post"], url_path="clock-in")
	def clock_in(self, request):
		hoy = timezone.localdate()
		if AttendanceRecord.objects.filter(employee=request.user, date=hoy, clock_out_time__isnull=True).exists():
			return Response({"detail": "Ya existe un attendance_record abierto para hoy."}, status=400)
		attendance_record = AttendanceRecord.objects.create(
			employee=request.user,
			branch=request.user.branch,
			date=hoy,
			clock_in_time=timezone.now(),
			recorded_by=request.user,
		)
		return Response(self.get_serializer(attendance_record).data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=["post"], url_path="clock-out")
	def clock_out(self, request, pk=None):
		attendance_record = self.get_object()
		if attendance_record.clock_out_time:
			return Response({"detail": "Este attendance_record ya tiene clock_out_time registrada."}, status=400)
		attendance_record.clock_out_time = timezone.now()
		attendance_record.save(update_fields=["clock_out_time", "updated_at"])
		return Response(self.get_serializer(attendance_record).data)

	@action(detail=True, methods=["patch"], url_path="correct")
	def correct(self, request, pk=None):
		attendance_record = self.get_object()
		serializer = self.get_serializer(attendance_record, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save(corrected_by=request.user)
		notify(
			attendance_record.employee,
			NotificationType.ATTENDANCE,
			f"Your attendance record for {attendance_record.date} was corrected.",
			link="/asistencia",
		)
		return Response(serializer.data)
