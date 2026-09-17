from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Marcaje
from .permissions import PuedeGestionarMarcaje
from .serializers import MarcajeSerializer


class MarcajeViewSet(viewsets.ModelViewSet):
    queryset = Marcaje.objects.select_related("empleado", "sucursal")
    serializer_class = MarcajeSerializer
    permission_classes = [PuedeGestionarMarcaje]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.rol == "admin_general":
            return queryset
        if user.rol == "gerente_sucursal":
            return queryset.filter(sucursal_id=user.sucursal_id)
        return queryset.filter(empleado=user)

    @action(detail=False, methods=["post"], url_path="marcar-entrada")
    def marcar_entrada(self, request):
        hoy = timezone.localdate()
        marcaje = Marcaje.objects.filter(
            empleado=request.user,
            fecha=hoy,
            salida__isnull=True,
        ).first()
        if marcaje:
            return Response(
                {"detail": "Ya existe un marcaje abierto para hoy."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        marcaje = Marcaje.objects.create(
            empleado=request.user,
            sucursal=request.user.sucursal,
            fecha=hoy,
            entrada=timezone.now(),
            registrado_por=request.user,
        )
        return Response(self.get_serializer(marcaje).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="marcar-salida")
    def marcar_salida(self, request, pk=None):
        marcaje = self.get_object()
        if marcaje.salida:
            return Response(
                {"detail": "Este marcaje ya tiene salida registrada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        marcaje.salida = timezone.now()
        marcaje.save(update_fields=["salida", "actualizado_en"])
        return Response(self.get_serializer(marcaje).data)

    @action(detail=True, methods=["patch"], url_path="corregir")
    def corregir(self, request, pk=None):
        marcaje = self.get_object()
        serializer = self.get_serializer(marcaje, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(corregido_por=request.user)
        return Response(serializer.data)
