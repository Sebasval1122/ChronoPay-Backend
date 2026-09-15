from rest_framework import viewsets, permissions
from .models import ReglaLaboral, DiaFestivo
from .serializers import ReglaLaboralSerializer, DiaFestivoSerializer


class EsAdminGeneral(permissions.BasePermission):
    """
    Solo el admin general puede crear/editar/eliminar reglas laborales.
    Cualquier usuario autenticado puede consultarlas (lectura).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and getattr(
            request.user, "rol", None
        ) == "admin_general"


class ReglaLaboralViewSet(viewsets.ModelViewSet):
    """
    CRUD de reglas laborales por país (horas extra, recargos, límites legales).
    """

    queryset = ReglaLaboral.objects.all()
    serializer_class = ReglaLaboralSerializer
    permission_classes = [EsAdminGeneral]

    def get_queryset(self):
        queryset = super().get_queryset()
        pais = self.request.query_params.get("pais")
        if pais:
            queryset = queryset.filter(pais__iexact=pais)
        return queryset


class DiaFestivoViewSet(viewsets.ModelViewSet):
    """
    CRUD de días festivos asociados a una regla laboral (país).
    """

    queryset = DiaFestivo.objects.all()
    serializer_class = DiaFestivoSerializer
    permission_classes = [EsAdminGeneral]

    def get_queryset(self):
        queryset = super().get_queryset()
        regla_laboral_id = self.request.query_params.get("regla_laboral")
        if regla_laboral_id:
            queryset = queryset.filter(regla_laboral_id=regla_laboral_id)
        return queryset