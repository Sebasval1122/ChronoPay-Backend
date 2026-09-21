from rest_framework import permissions, viewsets

from common.permissions import is_admin_or_same_branch

from .models import BranchBudget
from .serializers import BranchBudgetSerializer


class IsAdminOrBranchManager(permissions.BasePermission):
	def has_permission(self, request, view):
		return (
			request.user.is_authenticated
			and request.user.rol in {"admin_general", "gerente_sucursal"}
		)

	def has_object_permission(self, request, view, obj):
		return is_admin_or_same_branch(request.user, obj.branch_id)


class BranchBudgetViewSet(viewsets.ModelViewSet):
	queryset = BranchBudget.objects.select_related("branch", "created_by")
	serializer_class = BranchBudgetSerializer
	permission_classes = [IsAdminOrBranchManager]

	def get_queryset(self):
		queryset = super().get_queryset()
		if self.request.user.rol == "gerente_sucursal":
			return queryset.filter(branch_id=self.request.user.branch_id)
		return queryset

	def perform_create(self, serializer):
		branch_id = serializer.validated_data["branch"].id
		if not is_admin_or_same_branch(self.request.user, branch_id):
			from rest_framework.exceptions import PermissionDenied

			raise PermissionDenied("You can only manage budgets for your branch.")
		serializer.save(created_by=self.request.user)