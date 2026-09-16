from rest_framework import permissions


class EsAdminOGerente(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.rol in {"admin_general", "gerente_sucursal"}
        )


class EsPropioUsuarioOAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.pk == request.user.pk or request.user.rol == "admin_general":
            return True
        return (
            request.user.rol == "gerente_sucursal"
            and obj.sucursal_id == request.user.sucursal_id
        )