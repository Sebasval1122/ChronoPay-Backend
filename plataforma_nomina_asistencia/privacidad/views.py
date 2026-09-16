from rest_framework import viewsets

from .models import ConsentimientoDatos, PoliticaTratamiento
from .serializers import ConsentimientoDatosSerializer, PoliticaTratamientoSerializer


class PoliticaTratamientoViewSet(viewsets.ModelViewSet):
    queryset = PoliticaTratamiento.objects.all()
    serializer_class = PoliticaTratamientoSerializer


class ConsentimientoDatosViewSet(viewsets.ModelViewSet):
    queryset = ConsentimientoDatos.objects.all()
    serializer_class = ConsentimientoDatosSerializer