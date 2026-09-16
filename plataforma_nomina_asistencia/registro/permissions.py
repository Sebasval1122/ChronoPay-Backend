from rest_framework.permissions import BasePermission


class PuedeGestionarMarcaje(BasePermission):
    """Permite marcar al propio empleado y corregir a admin o gerente."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if view.action in {"corregir", "update", "partial_update", "destroy"}:
            if request.user.rol == "admin_general":
                return True
            return (
                request.user.rol == "gerente_sucursal"
                and obj.sucursal_id == request.user.sucursal_id
            )
        return obj.empleado_id == request.user.id
