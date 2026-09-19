from rest_framework import permissions, viewsets

from .models import DataConsent, DataPolicy
from .serializers import ConsentimientoDatosSerializer, PoliticaTratamientoSerializer


class PoliticaTratamientoViewSet(viewsets.ModelViewSet):
    queryset = DataPolicy.objects.all()
    serializer_class = PoliticaTratamientoSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.rol == "admin_general":
            return super().get_queryset()
        return super().get_queryset().filter(vigente=True)

    def perform_create(self, serializer):
        if self.request.user.rol != "admin_general":
            raise permissions.PermissionDenied(
                "Solo un administrador general puede publicar políticas."
            )
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.rol != "admin_general":
            raise permissions.PermissionDenied(
                "Solo un administrador general puede modificar políticas."
            )
        serializer.save()


class ConsentimientoDatosViewSet(viewsets.ModelViewSet):
    queryset = DataConsent.objects.all()
    serializer_class = ConsentimientoDatosSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)