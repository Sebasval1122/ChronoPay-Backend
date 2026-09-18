# ChronoPay-Backend

Plataforma para negocios tipo cadenas (múltiples sucursales) que permite registrar la hora de llegada de los usuarios/empleados y, a partir de esos datos, calcular automáticamente la nómina — incluyendo horas obligatorias, horas extra, recargos y prestaciones según la legislación de cada país.

## Funcionalidades

### 💰 Nómina y compensación
- **Cálculo automático de horas extra diurnas vs. nocturnas**: el sistema diferencia entre las horas trabajadas en horario diurno y nocturno, aplicando la tarifa correspondiente a cada una, ya que suelen pagarse de forma distinta.
- **Recargos por trabajo en días festivos/dominicales**: cálculo automático de los recargos aplicables cuando un empleado trabaja en día festivo o domingo.
- **Generación de comprobantes de pago (PDF) por empleado**: emisión automática de un desprendible de pago en PDF con el detalle de horas trabajadas, recargos, deducciones y salario neto.
- **Historial de cambios salariales por empleado**: registro histórico de cada ajuste salarial, con fecha y motivo, para trazabilidad y auditoría. *(Disponible en la API; todavía sin pantalla en el frontend.)*

### 🏢 Administración multi-empresa y multi-sucursal
- **Registro público de empresa**: una cadena nueva puede crear su cuenta y su primer administrador desde `/api/empresas/registro/`, con el rol fijado por el servidor (nunca por quien se registra).
- **Permisos por rol**: control de acceso diferenciado para tres niveles — admin general, gerente de sucursal y empleado — cada uno con permisos acordes a su función.
- **Configuración de reglas laborales según el país**: parametrización del cálculo de horas extra, recargos y prestaciones conforme a la normativa laboral de cada país donde opera el negocio.

### 📊 Reportes y planeación
- **Reportes exportables** (CSV de nómina, filtrado según el rol de quien lo pide). *(Disponible en la API; todavía sin pantalla en el frontend.)*
- **Solicitud de vacaciones/permisos**: los empleados solicitan vacaciones o permisos, con flujo de aprobación o rechazo por parte del gerente/admin. *(Disponible en la API; todavía sin pantalla en el frontend.)*

### 🚧 Prometido pero aún no construido
- Dashboard consolidado para ver todas las sucursales
- Dashboard de costos de nómina proyectados vs. reales
- Sistema de notificaciones (pago, turno, solicitud resuelta)
- Firma digital de producción para nómina electrónica DIAN (hoy usa firma de desarrollo)
- Retención en la fuente con la tabla real por UVT (hoy es una tarifa fija)

## Personas / Roles del sistema

### 🧑‍💼 Admin general
Responsable de toda la cadena, con visibilidad y control sobre todas las sucursales.

- Ver todas las sucursales y su información
- Crear, editar y eliminar sucursales
- Configurar las reglas laborales según el país (horas extra, recargos, prestaciones)
- Crear y gestionar usuarios de cualquier rol (admins, gerentes, empleados)
- Ver y editar el historial de cambios salariales de cualquier empleado
- Generar reportes en CSV
- Aprobar o rechazar cualquier solicitud de vacaciones/permisos

### 🏬 Gerente de sucursal
Responsable de la operación diaria de asistencia y nómina de su propia sucursal.

- Ver la asistencia y nómina de su sucursal
- Registrar y ajustar marcajes de asistencia de sus empleados (correcciones manuales)
- Ver el cálculo de nómina de su sucursal (horas extra, recargos por festivos/domingos)
- Generar y consultar los comprobantes de pago (PDF) de sus empleados
- Ver el historial de cambios salariales de los empleados de su sucursal
- Aprobar o rechazar solicitudes de vacaciones/permisos de su sucursal
- Generar reportes en CSV de su sucursal

### 👷 Empleado
Usuario final que registra su asistencia y consulta su propia información.

- Registrar su hora de llegada y salida (marcaje de asistencia)
- Consultar su historial de asistencia (horas trabajadas, horas extra, tardanzas)
- Consultar y descargar sus comprobantes de pago (PDF) — solo los propios, nunca los de un compañero
- Consultar su historial de cambios salariales propio
- Solicitar vacaciones o permisos y ver el estado de su solicitud

## Estructura del proyecto

```text
plataforma_nomina_asistencia/
├── manage.py
├── .env.example
├── requirements.txt
│
├── config/                         # Configuración global de Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── database/                       # Configuración y documentación de la BD
│   ├── __init__.py
│   ├── settings.py
│   ├── sqlite.py
│   ├── postgres.py
│   └── README.md
│
├── common/                         # Utilidades compartidas entre apps
│   ├── __init__.py
│   └── permissions.py              # ej. is_admin_or_same_branch, reutilizada por varias apps
│
├── empresas/                       # Registro público de empresa (multi-tenant)
│   ├── __init__.py
│   ├── models.py                   # Empresa
│   ├── serializers.py
│   ├── throttles.py                # límite de 5 registros/hora por IP
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── usuarios/                       # Usuarios, roles y autenticación
│   ├── __init__.py
│   ├── models.py                   # Usuario, HistorialSalarial
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py                     # CRUD de usuarios
│   ├── urls_auth.py                # Login y refresh JWT
│   └── migrations/
│
├── sucursales/                     # Sucursales de la cadena
│   ├── __init__.py
│   ├── models.py                   # Sucursal (con FK a Empresa)
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── asistencia/                     # Registro de marcajes (entrada/salida)
│   ├── __init__.py
│   ├── models.py                   # Marcaje
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── novedades/                      # Incapacidades, licencias y permisos
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── nomina/                         # Cálculo y consulta de nómina
│   ├── __init__.py
│   ├── models.py                   # Nomina, DetalleNomina
│   ├── calculo_horas.py            # Motor de cálculo: horas extra, recargos, diurno/nocturno
│   ├── services.py                 # generar_nomina()
│   ├── dian/                       # Integración con la DIAN (firma de desarrollo por ahora)
│   │   ├── __init__.py
│   │   ├── generador_xml.py
│   │   ├── firmador.py
│   │   └── cliente_dian.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── reglas_laborales/               # Reglas por país y días festivos
│   ├── __init__.py
│   ├── regla_laboral.py
│   ├── dia_festivo.py
│   ├── parametro_legal.py          # SMMLV y auxilio de transporte por año
│   ├── models.py                   # Re-exporta los modelos de arriba
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── comprobantes/                   # Generación de comprobantes PDF
│   ├── services.py
│   ├── views.py
│   └── urls.py
│
├── solicitudes/                    # Vacaciones y permisos
│   ├── __init__.py
│   ├── models.py                   # Solicitud, con flujo de aprobación/rechazo
│   ├── views.py                    # incluye el serializer (sin archivo aparte)
│   ├── urls.py
│   └── migrations/
│
├── privacidad/                     # Protección y consentimiento de datos
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
└── reportes/                       # Reportes exportables (CSV)
    ├── views.py
    └── urls.py
```

La base de datos por defecto para desarrollo es SQLite; la configuración de
Postgres se encuentra documentada en `database/README.md`.

## Roadmap

- [x] Definir modelo de datos (usuarios, turnos, marcajes, nómina, sucursales)
- [x] Implementar registro de asistencia
- [x] Implementar motor de cálculo de nómina (horas extra, recargos)
- [x] Implementar generación de comprobantes en PDF
- [x] Implementar módulo de vacaciones/permisos (API — falta la pantalla en el frontend)
- [x] Registro público multi-empresa, seguro (rol fijado por el servidor)
- [ ] Conectar en el frontend: solicitudes, historial salarial, reportes CSV
- [ ] Dashboard consolidado multi-sucursal
- [ ] Dashboard de costos de nómina proyectados vs. reales
- [ ] Sistema de notificaciones
- [ ] Módulo de hoja de vida y recomendación de crecimiento con IA (nunca recomienda desvinculación — esa decisión es siempre del dueño o gerente)
- [ ] Retención en la fuente con tabla real por UVT
- [ ] Firma digital de producción para nómina electrónica DIAN
- [ ] Verificación de correo / CAPTCHA en el registro público
- [ ] Cobro / plan de pago

---

