from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from sucursales.models import Sucursal
from usuarios.models import Rol, Usuario

from .plataforma_nomina_asistencia.empresas.models import Empresa


class RegistroEmpresaTests(APITestCase):
    url = "/api/empresas/registro/"

    def setUp(self):
        cache.clear()
        self.datos = {
            "nombre_empresa": "Cadena de Prueba",
            "nombre_admin": "Ana",
            "apellido_admin": "García",
            "email": "ana@cadena-prueba.test",
            "username": "ana_admin",
            "password": "UnaPasswordSegura-2026!",
        }

    def test_registro_crea_empresa_sucursal_y_admin(self):
        respuesta = self.client.post(self.url, self.datos, format="json")

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        empresa = Empresa.objects.get(pk=respuesta.data["empresa_id"])
        sucursal = Sucursal.objects.get(pk=respuesta.data["sucursal_id"])
        usuario = Usuario.objects.get(pk=respuesta.data["usuario_id"])

        self.assertEqual(empresa.nombre, self.datos["nombre_empresa"])
        self.assertEqual(empresa.email_contacto, self.datos["email"])
        self.assertEqual(sucursal.empresa, empresa)
        self.assertEqual(sucursal.nombre, "Principal")
        self.assertTrue(sucursal.codigo.startswith("PRINCIPAL-"))
        self.assertEqual(usuario.rol, Rol.ADMIN_GENERAL)
        self.assertEqual(usuario.sucursal, sucursal)
        self.assertTrue(usuario.check_password(self.datos["password"]))

    def test_registro_no_acepta_rol_ni_sucursal_en_el_body(self):
        datos = {
            **self.datos,
            "rol": Rol.ADMIN_GENERAL,
            "sucursal": 1,
        }

        respuesta = self.client.post(self.url, datos, format="json")

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("campos no permitidos", str(respuesta.data).lower())
        self.assertEqual(Empresa.objects.count(), 0)
        self.assertEqual(Usuario.objects.count(), 0)

    def test_registro_rechaza_password_debil(self):
        datos = {**self.datos, "password": "123"}

        respuesta = self.client.post(self.url, datos, format="json")

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", str(respuesta.data).lower())
        self.assertEqual(Empresa.objects.count(), 0)

    def test_registro_rechaza_username_o_email_existentes_con_mensaje_generico(self):
        Usuario.objects.create_user(
            username=self.datos["username"],
            email=self.datos["email"],
            password=self.datos["password"],
        )

        respuesta = self.client.post(self.url, self.datos, format="json")

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        mensaje = str(respuesta.data)
        self.assertIn("No fue posible completar el registro", mensaje)
        self.assertNotIn("ya existe", mensaje.lower())
        self.assertEqual(Empresa.objects.count(), 0)

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
        self.usuario = Usuario.objects.create_user(
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
