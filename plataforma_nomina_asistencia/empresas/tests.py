from datetime import date, datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from asistencia.models import Marcaje
from nomina.calculohoras import calcular_horas_marcaje
from nomina.dian.cliente_dian import enviar_documento
from nomina.dian.firmador import firmar_documento
from nomina.dian.generador_xml import generar_documento_soporte
from nomina.models import DetalleNomina, Nomina
from novedades.models import Incapacidad
from privacidad.models import ConsentimientoDatos, PoliticaTratamiento
from reglas_laborales.models import ReglaLaboral
from solicitudes.models import EstadoSolicitud, Solicitud, TipoSolicitud
from sucursales.models import Sucursal
from usuarios.models import Rol, Usuario

from .models import Empresa


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
        self.assertEqual(sucursal.empresa, empresa)
        self.assertEqual(sucursal.nombre, "Principal")
        self.assertTrue(sucursal.codigo.startswith("PRINCIPAL-"))
        self.assertEqual(usuario.rol, Rol.ADMIN_GENERAL)
        self.assertEqual(usuario.sucursal, sucursal)
        self.assertTrue(usuario.check_password(self.datos["password"]))

    def test_registro_rechaza_campos_privilegiados(self):
        datos = {**self.datos, "rol": Rol.ADMIN_GENERAL, "sucursal": 1}
        respuesta = self.client.post(self.url, datos, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("campos no permitidos", str(respuesta.data).lower())
        self.assertEqual(Empresa.objects.count(), 0)

    def test_registro_rechaza_password_debil_y_duplicados(self):
        debil = self.client.post(
            self.url, {**self.datos, "password": "123"}, format="json"
        )
        self.assertEqual(debil.status_code, status.HTTP_400_BAD_REQUEST)
        Usuario.objects.create_user(
            username=self.datos["username"],
            email=self.datos["email"],
            password=self.datos["password"],
        )
        duplicado = self.client.post(self.url, self.datos, format="json")
        self.assertEqual(duplicado.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No fue posible completar el registro", str(duplicado.data))

    def test_registro_aplica_throttle(self):
        respuestas = []
        for indice in range(6):
            datos = {
                **self.datos,
                "email": f"admin-{indice}@cadena-prueba.test",
                "username": f"admin_{indice}",
            }
            respuestas.append(self.client.post(self.url, datos, format="json"))
        self.assertEqual(respuestas[-1].status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(
            sum(r.status_code == status.HTTP_201_CREATED for r in respuestas), 5
        )


class DatosBaseTests(APITestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nombre="Cadena Base", email_contacto="base@cadena.test"
        )
        self.sucursal = Sucursal.objects.create(
            empresa=self.empresa, nombre="Principal", codigo="BASE-001"
        )
        self.otra_sucursal = Sucursal.objects.create(
            empresa=self.empresa, nombre="Norte", codigo="BASE-002"
        )
        self.admin = Usuario.objects.create_user(
            username="admin_base", email="admin@cadena.test",
            password="UnaPasswordSegura-2026!", rol=Rol.ADMIN_GENERAL,
            sucursal=self.sucursal,
        )
        self.gerente = Usuario.objects.create_user(
            username="gerente_base", email="gerente@cadena.test",
            password="UnaPasswordSegura-2026!", rol=Rol.GERENTE_SUCURSAL,
            sucursal=self.sucursal,
        )
        self.empleado = Usuario.objects.create_user(
            username="empleado_base", email="empleado@cadena.test",
            password="UnaPasswordSegura-2026!", rol=Rol.EMPLEADO,
            sucursal=self.sucursal, salario_actual=Decimal("3000000"),
        )

    def autenticar(self, usuario):
        self.client.force_authenticate(user=usuario)


class AutenticacionUsuariosTests(DatosBaseTests):
    def test_login_refresh_y_register_antiguo(self):
        login = self.client.post(
            "/api/auth/login/",
            {"username": "empleado_base", "password": "UnaPasswordSegura-2026!"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)
        refresh = self.client.post(
            "/api/auth/refresh/", {"refresh": login.data["refresh"]}, format="json"
        )
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.post("/api/auth/register/", {}, format="json").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_empleado_solo_consulta_su_me(self):
        self.autenticar(self.empleado)
        me = self.client.get("/api/usuarios/me/")
        lista = self.client.get("/api/usuarios/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["username"], self.empleado.username)
        self.assertEqual(lista.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_crea_usuario_y_cambia_salario(self):
        self.autenticar(self.admin)
        crear = self.client.post(
            "/api/usuarios/",
            {
                "username": "nuevo_empleado", "password": "OtraPasswordSegura-2026!",
                "first_name": "Nuevo", "last_name": "Empleado",
                "email": "nuevo@cadena.test", "rol": Rol.EMPLEADO,
                "sucursal": self.sucursal.id,
            }, format="json",
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        nuevo = Usuario.objects.get(username="nuevo_empleado")
        self.assertTrue(nuevo.check_password("OtraPasswordSegura-2026!"))
        cambio = self.client.post(
            f"/api/usuarios/{self.empleado.id}/cambiar_salario/",
            {"salario_nuevo": "3500000", "motivo": "Ajuste"}, format="json",
        )
        self.assertEqual(cambio.status_code, status.HTTP_200_OK)
        self.empleado.refresh_from_db()
        self.assertEqual(self.empleado.salario_actual, Decimal("3500000.00"))
        self.assertTrue(self.empleado.historial_salarial.filter(motivo="Ajuste").exists())


class SucursalesAsistenciaTests(DatosBaseTests):
    def test_crud_sucursal_y_codigo_unico(self):
        self.autenticar(self.admin)
        crear = self.client.post(
            "/api/sucursales/", {"nombre": "Sur", "codigo": "BASE-003"}, format="json"
        )
        duplicada = self.client.post(
            "/api/sucursales/", {"nombre": "Duplicada", "codigo": "BASE-001"}, format="json"
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicada.status_code, status.HTTP_400_BAD_REQUEST)

    def test_entrada_salida_y_marcaje_abierto_unico(self):
        self.autenticar(self.empleado)
        entrada = self.client.post("/api/asistencia/marcajes/marcar-entrada/")
        repetida = self.client.post("/api/asistencia/marcajes/marcar-entrada/")
        salida = self.client.post(
            f"/api/asistencia/marcajes/{entrada.data['id']}/marcar-salida/"
        )
        self.assertEqual(entrada.status_code, status.HTTP_201_CREATED)
        self.assertEqual(repetida.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(salida.status_code, status.HTTP_200_OK)
        self.assertEqual(salida.data["horas_trabajadas"], 0.0)

    def test_empleado_no_corrige_marcaje(self):
        marcaje = Marcaje.objects.create(
            empleado=self.empleado, sucursal=self.sucursal,
            entrada=timezone.now() - timedelta(hours=2), salida=timezone.now(),
        )
        self.autenticar(self.empleado)
        respuesta = self.client.patch(
            f"/api/asistencia/marcajes/{marcaje.id}/corregir/",
            {"motivo_correccion": "No autorizado"}, format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)


class ReglasNovedadesPrivacidadTests(DatosBaseTests):
    def test_admin_crea_regla_y_empleado_no_la_administra(self):
        self.autenticar(self.admin)
        crear = self.client.post(
            "/api/reglas-laborales/reglas/",
            {"pais": "Colombia", "hora_inicio_diurno": "06:00", "hora_inicio_nocturno": "19:00"},
            format="json",
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        self.autenticar(self.empleado)
        consulta = self.client.get("/api/reglas-laborales/reglas/")
        self.assertEqual(consulta.status_code, status.HTTP_200_OK)

    def test_novedad_se_asigna_al_usuario_autenticado(self):
        self.autenticar(self.empleado)
        respuesta = self.client.post(
            "/api/novedades/incapacidades/",
            {
                "usuario": self.empleado.id,
                "fecha_inicio": "2026-09-10",
                "fecha_fin": "2026-09-11",
                "descripcion": "Reposo",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["usuario"], self.empleado.id)
        self.assertEqual(Incapacidad.objects.filter(usuario=self.empleado).count(), 1)

    def test_politica_vigente_y_consentimiento(self):
        self.autenticar(self.admin)
        politica = self.client.post(
            "/api/privacidad/politicas/",
            {"version": "2026.1", "contenido": "Política vigente", "vigente": True},
            format="json",
        )
        self.assertEqual(politica.status_code, status.HTTP_201_CREATED)
        self.autenticar(self.empleado)
        consentimiento = self.client.post(
            "/api/privacidad/consentimientos/",
            {"politica": politica.data["id"], "aceptado": True}, format="json",
        )
        self.assertEqual(consentimiento.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ConsentimientoDatos.objects.filter(usuario=self.empleado).exists())


class SolicitudesNominaSalidasTests(DatosBaseTests):
    def setUp(self):
        super().setUp()
        self.regla = ReglaLaboral.objects.create(pais="Colombia", activo=True)
        self.nomina = Nomina.objects.create(
            sucursal=self.sucursal, periodo_inicio=date(2026, 9, 1), periodo_fin=date(2026, 9, 30)
        )

    def test_solicitud_se_crea_y_se_resuelve(self):
        self.autenticar(self.empleado)
        crear = self.client.post(
            "/api/solicitudes/",
            {"tipo": TipoSolicitud.PERMISO, "fecha_inicio": "2026-10-01", "fecha_fin": "2026-10-01", "motivo": "Cita"},
            format="json",
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        self.autenticar(self.gerente)
        resolver = self.client.post(
            f"/api/solicitudes/{crear.data['id']}/resolver/",
            {"estado": EstadoSolicitud.APROBADA}, format="json",
        )
        self.assertEqual(resolver.status_code, status.HTTP_200_OK)
        self.assertEqual(resolver.data["estado"], EstadoSolicitud.APROBADA)

    def test_nomina_se_genera_con_detalles_y_empleado_no_la_genera(self):
        Marcaje.objects.create(
            empleado=self.empleado, sucursal=self.sucursal, fecha=date(2026, 9, 15),
            entrada=timezone.make_aware(datetime(2026, 9, 15, 8, 0)),
            salida=timezone.make_aware(datetime(2026, 9, 15, 17, 0)),
        )
        self.autenticar(self.empleado)
        prohibida = self.client.post(f"/api/nomina/{self.nomina.id}/generar/")
        self.assertEqual(prohibida.status_code, status.HTTP_403_FORBIDDEN)
        self.autenticar(self.gerente)
        generada = self.client.post(f"/api/nomina/{self.nomina.id}/generar/")
        self.assertEqual(generada.status_code, status.HTTP_200_OK)
        self.nomina.refresh_from_db()
        self.assertEqual(self.nomina.estado, "generada")
        self.assertEqual(self.nomina.detalles.count(), 3)

    def test_comprobante_pdf_y_reporte_csv(self):
        detalle = DetalleNomina.objects.create(
            nomina=self.nomina, usuario=self.empleado, salario_base=Decimal("3000000"),
            total_neto=Decimal("2880000"),
        )
        self.autenticar(self.empleado)
        pdf = self.client.get(f"/api/comprobantes/{detalle.id}/pdf/")
        csv = self.client.get("/api/reportes/nomina.csv")
        self.assertEqual(pdf.status_code, status.HTTP_200_OK)
        self.assertTrue(pdf.content.startswith(b"%PDF"))
        self.assertEqual(csv.status_code, status.HTTP_200_OK)
        self.assertIn("Total neto", csv.content.decode("utf-8"))


class ServiciosNominaDianTests(DatosBaseTests):
    def test_calculo_horas_separa_jornada_ordinaria_y_extra(self):
        regla = ReglaLaboral.objects.create(pais="Colombia", activo=True)
        regla.refresh_from_db()
        marcaje = Marcaje(
            empleado=self.empleado,
            sucursal=self.sucursal,
            fecha=date(2026, 9, 15),
            entrada=timezone.make_aware(datetime(2026, 9, 15, 8, 0)),
            salida=timezone.make_aware(datetime(2026, 9, 15, 18, 0)),
        )

        desglose = calcular_horas_marcaje(marcaje, regla)

        self.assertEqual(desglose.ordinarias_diurnas, Decimal("8"))
        self.assertEqual(desglose.extra_diurnas, Decimal("2"))

    def test_utilidades_dian_generan_firman_y_envian_en_modo_desarrollo(self):
        documento = generar_documento_soporte({"identificador": "DOC-1", "total": "100"})
        firmado = firmar_documento(documento, "secreto-de-prueba")
        respuesta = enviar_documento(firmado)

        self.assertIn(b"DocumentoSoporte", documento)
        self.assertIn(b"firma-sha256", firmado)
        self.assertFalse(respuesta["enviado"])
        self.assertEqual(respuesta["modo"], "desarrollo")


class ConfiguracionApiTests(APITestCase):
    @override_settings(CORS_ALLOWED_ORIGINS=settings.CORS_ALLOWED_ORIGINS)
    def test_cors_incluye_origenes_frontend(self):
        self.assertIn("http://localhost:3000", settings.CORS_ALLOWED_ORIGINS)
        self.assertIn("http://localhost:5173", settings.CORS_ALLOWED_ORIGINS)
