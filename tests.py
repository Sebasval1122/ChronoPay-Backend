from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from branches.models import Branch
from users.models import Role, User

from .payroll_attendance.companies.models import Company


class RegistroEmpresaTests(APITestCase):
    url = "/api/companies/registro/"

    def setUp(self):
        cache.clear()
        self.datos = {
            "company_name": "Cadena de Prueba",
            "admin_first_name": "Ana",
            "admin_last_name": "García",
            "email": "ana@cadena-prueba.test",
            "username": "ana_admin",
            "password": "UnaPasswordSegura-2026!",
        }

    def test_registro_crea_empresa_sucursal_y_admin(self):
        respuesta = self.client.post(self.url, self.datos, format="json")

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        company = Company.objects.get(pk=respuesta.data["company_id"])
        branch = Branch.objects.get(pk=respuesta.data["branch_id"])
        user = User.objects.get(pk=respuesta.data["user_id"])

        self.assertEqual(company.name, self.datos["company_name"])
        self.assertEqual(company.contact_email, self.datos["email"])
        self.assertEqual(branch.company, company)
        self.assertEqual(branch.name, "Principal")
        self.assertTrue(branch.codigo.startswith("PRINCIPAL-"))
        self.assertEqual(user.rol, Role.ADMIN_GENERAL)
        self.assertEqual(user.branch, branch)
        self.assertTrue(user.check_password(self.datos["password"]))

    def test_registro_no_acepta_rol_ni_sucursal_en_el_body(self):
        datos = {
            **self.datos,
            "rol": Role.ADMIN_GENERAL,
            "branch": 1,
        }

        respuesta = self.client.post(self.url, datos, format="json")

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("campos no permitidos", str(respuesta.data).lower())
        self.assertEqual(Company.objects.count(), 0)
        self.assertEqual(User.objects.count(), 0)

    def test_registro_rechaza_password_debil(self):
        datos = {**self.datos, "password": "123"}

        respuesta = self.client.post(self.url, datos, format="json")

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", str(respuesta.data).lower())
        self.assertEqual(Company.objects.count(), 0)

    def test_registro_rechaza_username_o_email_existentes_con_mensaje_generico(self):
        User.objects.create_user(
            username=self.datos["username"],
            email=self.datos["email"],
            password=self.datos["password"],
        )

        respuesta = self.client.post(self.url, self.datos, format="json")

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        mensaje = str(respuesta.data)
        self.assertIn("No fue posible completar el registro", mensaje)
        self.assertNotIn("ya existe", mensaje.lower())
        self.assertEqual(Company.objects.count(), 0)

    def test_registro_publico_aplica_throttle_por_ip(self):
        respuestas = []
        for indice in range(6):
            datos = {
                **self.datos,
                "email": f"admin-{indice}@cadena-prueba.test",
                "username": f"admin_{indice}",
            }
            respuestas.append(self.client.post(self.url, datos, format="json"))

        self.assertEqual(respuestas[-1].status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(sum(response.status_code == status.HTTP_201_CREATED for response in respuestas), 5)


class AutenticacionEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="usuario_login",
            email="login@test.example",
            password="UnaPasswordSegura-2026!",
        )

    def test_login_y_refresh_siguen_disponibles(self):
        login = self.client.post(
            "/api/auth/login/",
            {"username": "usuario_login", "password": "UnaPasswordSegura-2026!"},
            format="json",
        )

        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)
        self.assertIn("refresh", login.data)

        refresh = self.client.post(
            "/api/auth/refresh/",
            {"refresh": login.data["refresh"]},
            format="json",
        )

        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh.data)

    def test_registro_antiguo_no_existe(self):
        respuesta = self.client.post("/api/auth/register/", {}, format="json")

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)


class ConfiguracionApiTests(APITestCase):
    @override_settings(CORS_ALLOWED_ORIGINS=settings.CORS_ALLOWED_ORIGINS)
    def test_cors_incluye_vite_y_create_react_app(self):
        self.assertIn("http://localhost:3000", settings.CORS_ALLOWED_ORIGINS)
        self.assertIn("http://localhost:5173", settings.CORS_ALLOWED_ORIGINS)
