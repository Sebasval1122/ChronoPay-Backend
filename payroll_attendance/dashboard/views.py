from calendar import monthrange
from decimal import Decimal

from django.db.models import Count, DecimalField, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.models import AttendanceRecord
from branches.models import Branch
from payroll.models import PayrollDetail
from work_events.models import Leave, Permission, SickLeave

from budgets.models import BranchBudget


class IsAdminOrBranchManager(permissions.BasePermission):
	def has_permission(self, request, view):
		return (
			request.user.is_authenticated
			and request.user.rol in {"admin_general", "gerente_sucursal"}
		)


class BranchDashboardView(APIView):
	permission_classes = [IsAdminOrBranchManager]

	def get(self, request):
		now = timezone.now()
		year = self._parse_positive_int(request.query_params.get("year"), now.year)
		month = self._parse_positive_int(request.query_params.get("month"), now.month)
		if month < 1 or month > 12:
			return Response({"detail": "month must be between 1 and 12."}, status=400)

		month_start = timezone.datetime(year, month, 1).date()
		month_end = timezone.datetime(year, month, monthrange(year, month)[1]).date()
		payroll_totals = PayrollDetail.objects.filter(
			payroll__branch_id=OuterRef("pk"),
			payroll__period_start__year=year,
			payroll__period_start__month=month,
		).values("payroll__branch_id").annotate(
			total=Sum("net_total"),
			overtime=Sum("overtime_hours"),
		).values("total", "overtime")
		budget = BranchBudget.objects.filter(
			branch_id=OuterRef("pk"), year=year, month=month
		).values("budgeted_amount")[:1]

		def event_count(model):
			return Subquery(
				model.objects.filter(
					user__branch_id=OuterRef("pk"),
					approved=True,
					start_date__lte=month_end,
					end_date__gte=month_start,
				).values("user__branch_id").annotate(
					count=Count("id"),
				).values("count")[:1],
			)

		branches = Branch.objects.annotate(
			active_employee_count=Count(
				"users",
				filter=Q(users__rol="employee", users__active=True),
			),
			real_payroll_total=Coalesce(
				Subquery(payroll_totals.values("total")[:1]),
				Value(Decimal("0.00")),
				output_field=DecimalField(max_digits=14, decimal_places=2),
			),
			total_overtime_hours=Coalesce(
				Subquery(payroll_totals.values("overtime")[:1]),
				Value(Decimal("0.00")),
				output_field=DecimalField(max_digits=8, decimal_places=2),
			),
			budgeted_amount=Subquery(budget),
			work_events_count=Coalesce(
				event_count(SickLeave) + event_count(Leave) + event_count(Permission),
				Value(0),
			),
			attendance_records_count=Count(
				"attendance_records",
				filter=Q(
					attendance_records__date__gte=month_start,
					attendance_records__date__lte=month_end,
				),
			),
		)
		if request.user.rol == "gerente_sucursal":
			branches = branches.filter(id=request.user.branch_id)

		data = []
		for branch in branches:
			budgeted_amount = branch.budgeted_amount
			data.append(
				{
					"branch_id": branch.id,
					"branch_name": branch.name,
					"active_employee_count": branch.active_employee_count,
					"real_payroll_total": branch.real_payroll_total,
					"budgeted_amount": budgeted_amount,
					"budget_difference": (
						budgeted_amount - branch.real_payroll_total
						if budgeted_amount is not None else None
					),
					"total_overtime_hours": branch.total_overtime_hours,
					"work_events_count": branch.work_events_count,
					"attendance_records_count": branch.attendance_records_count,
				}
			)
		return Response(data)

	@staticmethod
	def _parse_positive_int(value, default):
		try:
			return int(value) if value is not None else default
		except (TypeError, ValueError):
			return default