from rest_framework.permissions import BasePermission

from common.permissions import is_admin_or_same_branch


class PuedeGestionarMarcaje(BasePermission):
	def has_permission(self, request, view):
		return bool(request.user and request.user.is_authenticated)

	def has_object_permission(self, request, view, obj):
		if view.action in {"corregir", "partial_update", "update", "destroy"}:
			return is_admin_or_same_branch(request.user, obj.sucursal_id)
		return obj.empleado_id == request.user.id
