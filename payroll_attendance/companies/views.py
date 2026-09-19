import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from sucursales.models import Sucursal

from .models import Empresa
from .serializers import RegistroEmpresaSerializer
from .throttles import RegistroEmpresaThrottle


Usuario = get_user_model()


class RegistroEmpresaView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegistroEmpresaThrottle]

    def post(self, request):
        serializer = RegistroEmpresaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        try:
            with transaction.atomic():
                empresa = Empresa.objects.create(
                    nombre=datos["nombre_empresa"],
                    email_contacto=datos["email"],
                )
                sucursal = Sucursal.objects.create(
                    empresa=empresa,
                    nombre="Principal",
                    codigo=self._generar_codigo_sucursal(),
                )
                usuario = Usuario(
                    username=datos["username"],
                    first_name=datos["nombre_admin"],
                    last_name=datos["apellido_admin"],
                    email=datos["email"],
                    rol="admin_general",
                    sucursal=sucursal,
                )
                usuario.set_password(datos["password"])
                usuario.save()
        except IntegrityError:
            return Response(
                {"detail": "No fue posible completar el registro con los datos proporcionados."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "Empresa registrada correctamente.",
                "empresa_id": empresa.id,
                "sucursal_id": sucursal.id,
                "usuario_id": usuario.id,
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _generar_codigo_sucursal():
        while True:
            codigo = f"PRINCIPAL-{uuid.uuid4().hex[:20]}"
            if not Sucursal.objects.filter(codigo=codigo).exists():
                return codigo
