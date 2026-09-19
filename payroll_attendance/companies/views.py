import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from branches.models import Branch

from .models import Company
from .serializers import CompanyRegistrationSerializer
from .throttles import CompanyRegistrationThrottle


User = get_user_model()


class CompanyRegistrationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [CompanyRegistrationThrottle]

    def post(self, request):
        serializer = CompanyRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data

        try:
            with transaction.atomic():
                company = Company.objects.create(
                    name=datos["company_name"],
                    contact_email=datos["email"],
                )
                branch = Branch.objects.create(
                    company=company,
                    name="Principal",
                    codigo=self._generate_branch_code(),
                )
                user = User(
                    username=datos["username"],
                    first_name=datos["admin_first_name"],
                    last_name=datos["admin_last_name"],
                    email=datos["email"],
                    rol="admin_general",
                    branch=branch,
                )
                user.set_password(datos["password"])
                user.save()
        except IntegrityError:
            return Response(
                {"detail": "No fue posible completar el registro con los datos proporcionados."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "Company registrada correctamente.",
                "company_id": company.id,
                "branch_id": branch.id,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _generate_branch_code():
        while True:
            codigo = f"PRINCIPAL-{uuid.uuid4().hex[:20]}"
            if not Branch.objects.filter(codigo=codigo).exists():
                return codigo
