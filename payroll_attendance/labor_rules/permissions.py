from rest_framework import permissions


class IsGeneralAdmin(permissions.BasePermission):
    """Permite lectura a users autenticados y escritura solo a admin general."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "rol", None) == "admin_general"
        )
