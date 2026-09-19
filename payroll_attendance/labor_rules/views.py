from rest_framework import viewsets

from .models import DiaFestivo, ReglaLaboral
from .permissions import EsAdminGeneral
from .serializers import DiaFestivoSerializer, ReglaLaboralSerializer


class ReglaLaboralViewSet(viewsets.ModelViewSet):
    """CRUD de reglas laborales por país."""

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
    """CRUD de días festivos asociados a una regla laboral."""

    queryset = DiaFestivo.objects.all()
    serializer_class = DiaFestivoSerializer
    permission_classes = [EsAdminGeneral]

    def get_queryset(self):
        queryset = super().get_queryset()
        regla_laboral_id = self.request.query_params.get("regla_laboral")
        if regla_laboral_id:
            queryset = queryset.filter(regla_laboral_id=regla_laboral_id)
        return queryset
