from django.db import transaction
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Usuario, HistorialSalarial
from .serializers import (
    UsuarioSerializer,
    CrearUsuarioSerializer,
    CambiarSalarioSerializer,
    HistorialSalarialSerializer,
)
from .permissions import EsAdminOGerente, EsPropioUsuarioOAdmin


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de usuarios. La visibilidad depende del rol:
    - admin_general: ve y gestiona todos los usuarios
    - gerente_sucursal: ve y gestiona solo los usuarios de su sucursal
    - empleado: solo puede ver/editar su propia información (vía /me)
    """

    queryset = Usuario.objects.all()
    permission_classes = [EsAdminOGerente, EsPropioUsuarioOAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return CrearUsuarioSerializer
        return UsuarioSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.rol == "gerente_sucursal":
            queryset = queryset.filter(sucursal=user.sucursal)
        return queryset

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Devuelve la información del usuario autenticado."""
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[EsAdminOGerente])
    def cambiar_salario(self, request, pk=None):
        """
        Cambia el salario de un usuario y deja el registro en el
        historial salarial (trazabilidad del cambio).
        """
        usuario = self.get_object()
        serializer = CambiarSalarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        salario_anterior = usuario.salario_actual
        salario_nuevo = serializer.validated_data["salario_nuevo"]
        motivo = serializer.validated_data.get("motivo", "")

        with transaction.atomic():
            usuario.salario_actual = salario_nuevo
            usuario.save(update_fields=["salario_actual"])

            HistorialSalarial.objects.create(
                usuario=usuario,
                salario_anterior=salario_anterior,
                salario_nuevo=salario_nuevo,
                motivo=motivo,
                registrado_por=request.user,
            )

        return Response(UsuarioSerializer(usuario).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[EsAdminOGerente])
    def historial_salarial(self, request, pk=None):
        """Devuelve el historial de cambios salariales de un usuario."""
        usuario = self.get_object()
        historial = usuario.historial_salarial.all()
        serializer = HistorialSalarialSerializer(historial, many=True)
        return Response(serializer.data)