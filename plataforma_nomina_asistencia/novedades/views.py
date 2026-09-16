from rest_framework import viewsets

from .models import Incapacidad, Licencia, Permiso
from .serializers import (
    IncapacidadSerializer,
    LicenciaSerializer,
    PermisoSerializer,
)


class IncapacidadViewSet(viewsets.ModelViewSet):
    queryset = Incapacidad.objects.all()
    serializer_class = IncapacidadSerializer


class LicenciaViewSet(viewsets.ModelViewSet):
    queryset = Licencia.objects.all()
    serializer_class = LicenciaSerializer


class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer