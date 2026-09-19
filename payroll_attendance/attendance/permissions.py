from rest_framework.permissions import BasePermission

from common.permissions import is_admin_or_same_branch


class CanManageAttendance(BasePermission):
	def has_permission(self, request, view):
		return bool(request.user and request.user.is_authenticated)

	def has_object_permission(self, request, view, obj):
		if view.action in {"correct", "partial_update", "update", "destroy"}:
			return is_admin_or_same_branch(request.user, obj.branch_id)
		return obj.employee_id == request.user.id
