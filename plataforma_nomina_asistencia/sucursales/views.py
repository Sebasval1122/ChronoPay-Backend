from rest_framework import viewsets

from .models import Sucursal
from .serializers import SucursalSerializer


class SucursalViewSet(viewsets.ModelViewSet):
    """CRUD de sucursales."""

    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
