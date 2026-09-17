from rest_framework import permissions, viewsets

from .models import ConsentimientoDatos, PoliticaTratamiento
from .serializers import ConsentimientoDatosSerializer, PoliticaTratamientoSerializer


class PoliticaTratamientoViewSet(viewsets.ModelViewSet):
    queryset = PoliticaTratamiento.objects.all()
    serializer_class = PoliticaTratamientoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(activa=True)


class ConsentimientoDatosViewSet(viewsets.ModelViewSet):
    queryset = ConsentimientoDatos.objects.all()
    serializer_class = ConsentimientoDatosSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)