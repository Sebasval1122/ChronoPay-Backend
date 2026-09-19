from django.db import transaction
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User, SalaryHistory
from .serializers import (
    UserSerializer,
    CreateUserSerializer,
    ChangeSalarySerializer,
    SalaryHistorySerializer,
)
from .permissions import IsAdminOrManager, IsSelfOrAdmin


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de users. La visibilidad depende del rol:
    - admin_general: ve y gestiona todos los users
    - gerente_sucursal: ve y gestiona solo los users de su branch
    - employee: solo puede ver/editar su propia información (vía /me)
    """

    queryset = User.objects.all()
    permission_classes = [IsAdminOrManager, IsSelfOrAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.rol == "gerente_sucursal":
            queryset = queryset.filter(branch=user.branch)
        return queryset

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Devuelve la información del user autenticado."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrManager])
    def cambiar_salario(self, request, pk=None):
        """
        Cambia el salario de un user y deja el registro en el
        historial salarial (trazabilidad del cambio).
        """
        user = self.get_object()
        serializer = ChangeSalarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        previous_salary = user.current_salary
        new_salary = serializer.validated_data["new_salary"]
        reason = serializer.validated_data.get("reason", "")

        with transaction.atomic():
            user.current_salary = new_salary
            user.save(update_fields=["current_salary"])

            SalaryHistory.objects.create(
                user=user,
                previous_salary=previous_salary,
                new_salary=new_salary,
                reason=reason,
                recorded_by=request.user,
            )

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsAdminOrManager])
    def historial_salarial(self, request, pk=None):
        """Devuelve el historial de cambios salariales de un user."""
        user = self.get_object()
        historial = user.historial_salarial.all()
        serializer = SalaryHistorySerializer(historial, many=True)
        return Response(serializer.data)