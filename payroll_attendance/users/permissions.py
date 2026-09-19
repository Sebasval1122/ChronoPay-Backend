from rest_framework import permissions

from common.permissions import is_admin_or_same_branch


class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.rol in {"admin_general", "gerente_sucursal"}
        )


class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.pk == request.user.pk:
            return True
        return is_admin_or_same_branch(request.user, obj.branch_id)