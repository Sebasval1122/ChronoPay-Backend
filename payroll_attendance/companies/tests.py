from datetime import date, datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from attendance.models import AttendanceRecord
from payroll.hours_calculation import calculate_attendance_hours
from payroll.dian.dian_client import send_document
from payroll.dian.signer import sign_document
from payroll.dian.xml_generator import generate_support_document
from payroll.models import PayrollDetail, Payroll
from work_events.models import SickLeave
from privacy.models import DataConsent, DataPolicy
from labor_rules.models import LaborRule
from time_off_requests.models import RequestStatus, Request, RequestType
from branches.models import Branch
from users.models import Role, User

from .models import Company


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
        self.assertEqual(branch.company, company)
        self.assertEqual(branch.name, "Principal")
        self.assertTrue(branch.codigo.startswith("PRINCIPAL-"))
        self.assertEqual(user.rol, Role.ADMIN_GENERAL)
        self.assertEqual(user.branch, branch)
        self.assertTrue(user.check_password(self.datos["password"]))

    def test_registro_rechaza_campos_privilegiados(self):
        datos = {**self.datos, "rol": Role.ADMIN_GENERAL, "branch": 1}
        respuesta = self.client.post(self.url, datos, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("campos no permitidos", str(respuesta.data).lower())
        self.assertEqual(Company.objects.count(), 0)

    def test_registro_rechaza_password_debil_y_duplicados(self):
        debil = self.client.post(
            self.url, {**self.datos, "password": "123"}, format="json"
        )
        self.assertEqual(debil.status_code, status.HTTP_400_BAD_REQUEST)
        User.objects.create_user(
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
        self.company = Company.objects.create(
            name="Cadena Base", contact_email="base@cadena.test"
        )
        self.branch = Branch.objects.create(
            company=self.company, name="Principal", codigo="BASE-001"
        )
        self.otra_sucursal = Branch.objects.create(
            company=self.company, name="Norte", codigo="BASE-002"
        )
        self.admin = User.objects.create_user(
            username="admin_base", email="admin@cadena.test",
            password="UnaPasswordSegura-2026!", rol=Role.ADMIN_GENERAL,
            branch=self.branch,
        )
        self.gerente = User.objects.create_user(
            username="gerente_base", email="gerente@cadena.test",
            password="UnaPasswordSegura-2026!", rol=Role.GERENTE_SUCURSAL,
            branch=self.branch,
        )
        self.employee = User.objects.create_user(
            username="empleado_base", email="employee@cadena.test",
            password="UnaPasswordSegura-2026!", rol=Role.EMPLEADO,
            branch=self.branch, current_salary=Decimal("3000000"),
        )

    def autenticar(self, user):
        self.client.force_authenticate(user=user)


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
        self.autenticar(self.employee)
        me = self.client.get("/api/users/me/")
        lista = self.client.get("/api/users/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["username"], self.employee.username)
        self.assertEqual(lista.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_crea_usuario_y_cambia_salario(self):
        self.autenticar(self.admin)
        crear = self.client.post(
            "/api/users/",
            {
                "username": "nuevo_empleado", "password": "OtraPasswordSegura-2026!",
                "first_name": "Nuevo", "last_name": "Empleado",
                "email": "nuevo@cadena.test", "rol": Role.EMPLEADO,
                "branch": self.branch.id,
            }, format="json",
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        nuevo = User.objects.get(username="nuevo_empleado")
        self.assertTrue(nuevo.check_password("OtraPasswordSegura-2026!"))
        cambio = self.client.post(
            f"/api/users/{self.employee.id}/cambiar_salario/",
            {"new_salary": "3500000", "reason": "Ajuste"}, format="json",
        )
        self.assertEqual(cambio.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.current_salary, Decimal("3500000.00"))
        self.assertTrue(self.employee.historial_salarial.filter(reason="Ajuste").exists())


class SucursalesAsistenciaTests(DatosBaseTests):
    def test_crud_sucursal_y_codigo_unico(self):
        self.autenticar(self.admin)
        crear = self.client.post(
            "/api/branches/", {"name": "Sur", "codigo": "BASE-003"}, format="json"
        )
        duplicada = self.client.post(
            "/api/branches/", {"name": "Duplicada", "codigo": "BASE-001"}, format="json"
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicada.status_code, status.HTTP_400_BAD_REQUEST)

    def test_entrada_salida_y_marcaje_abierto_unico(self):
        self.autenticar(self.employee)
        clock_in_time = self.client.post("/api/attendance/marcajes/clock-in/")
        repetida = self.client.post("/api/attendance/marcajes/clock-in/")
        clock_out_time = self.client.post(
            f"/api/attendance/marcajes/{clock_in_time.data['id']}/clock-out/"
        )
        self.assertEqual(clock_in_time.status_code, status.HTTP_201_CREATED)
        self.assertEqual(repetida.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(clock_out_time.status_code, status.HTTP_200_OK)
        self.assertEqual(clock_out_time.data["worked_hours"], 0.0)

    def test_empleado_no_corrige_marcaje(self):
        marcaje = AttendanceRecord.objects.create(
            employee=self.employee, branch=self.branch,
            clock_in_time=timezone.now() - timedelta(hours=2), clock_out_time=timezone.now(),
        )
        self.autenticar(self.employee)
        respuesta = self.client.patch(
            f"/api/attendance/marcajes/{marcaje.id}/correct/",
            {"correction_reason": "No autorizado"}, format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)


class ReglasNovedadesPrivacidadTests(DatosBaseTests):
    def test_admin_crea_regla_y_empleado_no_la_administra(self):
        self.autenticar(self.admin)
        crear = self.client.post(
            "/api/reglas-laborales/reglas/",
            {"country": "Colombia", "daytime_start": "06:00", "nighttime_start": "19:00"},
            format="json",
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        self.autenticar(self.employee)
        consulta = self.client.get("/api/reglas-laborales/reglas/")
        self.assertEqual(consulta.status_code, status.HTTP_200_OK)

    def test_novedad_se_asigna_al_usuario_autenticado(self):
        self.autenticar(self.employee)
        respuesta = self.client.post(
            "/api/work_events/sickleavees/",
            {
                "user": self.employee.id,
                "start_date": "2026-09-10",
                "end_date": "2026-09-11",
                "description": "Reposo",
            },
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["user"], self.employee.id)
        self.assertEqual(SickLeave.objects.filter(user=self.employee).count(), 1)

    def test_politica_vigente_y_consentimiento(self):
        self.autenticar(self.admin)
        policy = self.client.post(
            "/api/privacy/politicas/",
            {"version": "2026.1", "content": "Política vigente", "vigente": True},
            format="json",
        )
        self.assertEqual(policy.status_code, status.HTTP_201_CREATED)
        self.autenticar(self.employee)
        consentimiento = self.client.post(
            "/api/privacy/consentimientos/",
            {"policy": policy.data["id"], "aceptado": True}, format="json",
        )
        self.assertEqual(consentimiento.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DataConsent.objects.filter(user=self.employee).exists())


class SolicitudesNominaSalidasTests(DatosBaseTests):
    def setUp(self):
        super().setUp()
        self.regla = LaborRule.objects.create(country="Colombia", active=True)
        self.payroll = Payroll.objects.create(
            branch=self.branch, period_start=date(2026, 9, 1), period_end=date(2026, 9, 30)
        )

    def test_request_se_crea_y_se_resuelve(self):
        self.autenticar(self.employee)
        crear = self.client.post(
            "/api/time_off_requests/",
            {"type": RequestType.PERMISO, "start_date": "2026-10-01", "end_date": "2026-10-01", "reason": "Cita"},
            format="json",
        )
        self.assertEqual(crear.status_code, status.HTTP_201_CREATED)
        self.autenticar(self.gerente)
        resolve = self.client.post(
            f"/api/time_off_requests/{crear.data['id']}/resolve/",
            {"status": RequestStatus.APROBADA}, format="json",
        )
        self.assertEqual(resolve.status_code, status.HTTP_200_OK)
        self.assertEqual(resolve.data["status"], RequestStatus.APROBADA)

    def test_nomina_se_genera_con_detalles_y_empleado_no_la_genera(self):
        AttendanceRecord.objects.create(
            employee=self.employee, branch=self.branch, date=date(2026, 9, 15),
            clock_in_time=timezone.make_aware(datetime(2026, 9, 15, 8, 0)),
            clock_out_time=timezone.make_aware(datetime(2026, 9, 15, 17, 0)),
        )
        self.autenticar(self.employee)
        prohibida = self.client.post(f"/api/payroll/{self.payroll.id}/generar/")
        self.assertEqual(prohibida.status_code, status.HTTP_403_FORBIDDEN)
        self.autenticar(self.gerente)
        generada = self.client.post(f"/api/payroll/{self.payroll.id}/generar/")
        self.assertEqual(generada.status_code, status.HTTP_200_OK)
        self.payroll.refresh_from_db()
        self.assertEqual(self.payroll.status, "generada")
        self.assertEqual(self.payroll.detalles.count(), 3)

    def test_empleado_solo_ve_su_detalle_de_nomina(self):
        otro_empleado = User.objects.create_user(
            username="otro_empleado_nomina",
            email="otro-employee@cadena.test",
            password="UnaPasswordSegura-2026!",
            rol=Role.EMPLEADO,
            branch=self.branch,
        )
        PayrollDetail.objects.create(
            payroll=self.payroll,
            user=self.employee,
            base_salary=Decimal("3000000"),
        )
        PayrollDetail.objects.create(
            payroll=self.payroll,
            user=otro_empleado,
            base_salary=Decimal("5000000"),
        )

        self.autenticar(self.employee)
        lista = self.client.get("/api/payroll/")
        detalle = self.client.get(f"/api/payroll/{self.payroll.id}/")

        for respuesta in (lista, detalle):
            self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
            if isinstance(respuesta.data, dict) and "results" in respuesta.data:
                nominas = respuesta.data["results"]
            elif isinstance(respuesta.data, dict):
                nominas = [respuesta.data]
            else:
                nominas = respuesta.data
            detalles = nominas[0]["detalles"]
            self.assertEqual(len(detalles), 1)
            self.assertEqual(detalles[0]["user"], self.employee.id)
            self.assertEqual(detalles[0]["base_salary"], "3000000.00")
            self.assertNotIn("5000000.00", str(respuesta.data))

        self.autenticar(self.gerente)
        respuesta_gerente = self.client.get(f"/api/payroll/{self.payroll.id}/")
        self.assertEqual(respuesta_gerente.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta_gerente.data["detalles"]), 2)

    def test_comprobante_pdf_y_reporte_csv(self):
        detalle = PayrollDetail.objects.create(
            payroll=self.payroll, user=self.employee, base_salary=Decimal("3000000"),
            net_total=Decimal("2880000"),
        )
        self.autenticar(self.employee)
        pdf = self.client.get(f"/api/pay_slips/{detalle.id}/pdf/")
        csv = self.client.get("/api/reports/payroll.csv")
        self.assertEqual(pdf.status_code, status.HTTP_200_OK)
        self.assertTrue(pdf.content.startswith(b"%PDF"))
        self.assertEqual(csv.status_code, status.HTTP_200_OK)
        self.assertIn("Total neto", csv.content.decode("utf-8"))


class ServiciosNominaDianTests(DatosBaseTests):
    def test_calculo_horas_separa_jornada_ordinaria_y_extra(self):
        regla = LaborRule.objects.create(country="Colombia", active=True)
        regla.refresh_from_db()
        marcaje = AttendanceRecord(
            employee=self.employee,
            branch=self.branch,
            date=date(2026, 9, 15),
            clock_in_time=timezone.make_aware(datetime(2026, 9, 15, 8, 0)),
            clock_out_time=timezone.make_aware(datetime(2026, 9, 15, 18, 0)),
        )

        desglose = calculate_attendance_hours(marcaje, regla)

        self.assertEqual(desglose.regular_day_hours, Decimal("8"))
        self.assertEqual(desglose.daytime_overtime_hours, Decimal("2"))

    def test_utilidades_dian_generan_firman_y_envian_en_modo_desarrollo(self):
        documento = generate_support_document({"identificador": "DOC-1", "total": "100"})
        firmado = sign_document(documento, "secreto-de-prueba")
        respuesta = send_document(firmado)

        self.assertIn(b"DocumentoSoporte", documento)
        self.assertIn(b"firma-sha256", firmado)
        self.assertFalse(respuesta["enviado"])
        self.assertEqual(respuesta["modo"], "desarrollo")


class ConfiguracionApiTests(APITestCase):
    @override_settings(CORS_ALLOWED_ORIGINS=settings.CORS_ALLOWED_ORIGINS)
    def test_cors_incluye_origenes_frontend(self):
        self.assertIn("http://localhost:3000", settings.CORS_ALLOWED_ORIGINS)
        self.assertIn("http://localhost:5173", settings.CORS_ALLOWED_ORIGINS)
