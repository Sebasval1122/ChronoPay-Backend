from rest_framework import viewsets

from .models import Holiday, LaborRule
from .permissions import IsGeneralAdmin
from .serializers import HolidaySerializer, LaborRuleSerializer


class LaborRuleViewSet(viewsets.ModelViewSet):
    """CRUD de rules laborales por país."""

    queryset = LaborRule.objects.all()
    serializer_class = LaborRuleSerializer
    permission_classes = [IsGeneralAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(pais__iexact=country)
        return queryset


class HolidayViewSet(viewsets.ModelViewSet):
    """CRUD de días festivos asociados a una labor_rule laboral."""

    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsGeneralAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        regla_laboral_id = self.request.query_params.get("labor_rule")
        if regla_laboral_id:
            queryset = queryset.filter(regla_laboral_id=regla_laboral_id)
        return queryset
