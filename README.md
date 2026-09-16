# ChronoPay-Backend

Plataforma para negocios tipo cadenas (múltiples sucursales) que permite registrar la hora de llegada de los usuarios/empleados y, a partir de esos datos, calcular automáticamente la nómina — incluyendo horas obligatorias, horas extra, recargos y prestaciones según la legislación de cada país.

## Funcionalidades

### 💰 Nómina y compensación
- **Cálculo automático de horas extra diurnas vs. nocturnas**: el sistema diferencia entre las horas trabajadas en horario diurno y nocturno, aplicando la tarifa correspondiente a cada una, ya que suelen pagarse de forma distinta.
- **Recargos por trabajo en días festivos/dominicales**: cálculo automático de los recargos aplicables cuando un empleado trabaja en día festivo o domingo.
- **Generación de comprobantes de pago (PDF) por empleado**: emisión automática de un desprendible de pago en PDF con el detalle de horas trabajadas, recargos, deducciones y salario neto.
- **Historial de cambios salariales por empleado**: registro histórico de cada ajuste salarial, con fecha y motivo, para trazabilidad y auditoría.

### 🏢 Administración multi-sucursal
- **Dashboard consolidado para ver todas las sucursales**: vista centralizada con el estado de asistencia y nómina de toda la cadena.
- **Permisos por rol**: control de acceso diferenciado para tres niveles — admin general, gerente de sucursal y empleado — cada uno con permisos acordes a su función.
- **Configuración de reglas laborales según el país**: parametrización del cálculo de horas extra, recargos y prestaciones conforme a la normativa laboral de cada país donde opera el negocio.

### 📊 Reportes y planeación
- **Reportes exportables para auditorías o entes gubernamentales**: generación de reportes en formatos estándar para cumplir con requerimientos legales y auditorías.
- **Dashboard de costos de nómina proyectados vs. reales**: comparación entre el gasto de nómina estimado y el efectivamente ejecutado, por sucursal o consolidado.
- **Solicitud de vacaciones/permisos desde la misma plataforma**: módulo para que los empleados soliciten vacaciones o permisos, con flujo de aprobación por parte del gerente/admin.

## Personas / Roles del sistema

### 🧑‍💼 Admin general
Responsable de toda la cadena, con visibilidad y control sobre todas las sucursales.

- Ver el dashboard consolidado de todas las sucursales
- Crear, editar y eliminar sucursales
- Configurar las reglas laborales según el país (horas extra, recargos, prestaciones)
- Crear y gestionar usuarios de cualquier rol (admins, gerentes, empleados)
- Ver y editar el historial de cambios salariales de cualquier empleado
- Generar y exportar reportes para auditorías o entes gubernamentales
- Ver el dashboard de costos de nómina proyectados vs. reales de toda la cadena
- Aprobar o rechazar solicitudes de vacaciones/permisos escaladas por gerentes

### 🏬 Gerente de sucursal
Responsable de la operación diaria de asistencia y nómina de su propia sucursal.

- Ver el dashboard de asistencia y nómina de su sucursal
- Registrar y ajustar marcajes de asistencia de sus empleados (correcciones manuales)
- Ver el cálculo de nómina de su sucursal (horas extra, recargos por festivos/domingos)
- Generar y consultar los comprobantes de pago (PDF) de sus empleados
- Ver el historial de cambios salariales de los empleados de su sucursal
- Aprobar o rechazar solicitudes de vacaciones/permisos de su sucursal
- Ver el comparativo de costos de nómina proyectados vs. reales de su sucursal
- Exportar reportes locales de su sucursal

### 👷 Empleado
Usuario final que registra su asistencia y consulta su propia información.

- Registrar su hora de llegada y salida (marcaje de asistencia)
- Consultar su historial de asistencia (horas trabajadas, horas extra, tardanzas)
- Consultar y descargar sus comprobantes de pago (PDF)
- Consultar su historial de cambios salariales propio
- Solicitar vacaciones o permisos y ver el estado de su solicitud
- Recibir notificaciones sobre su pago, turno o solicitud aprobada/rechazada

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
├── usuarios/                       # Usuarios, roles y autenticación
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py                     # CRUD de usuarios
│   ├── urls_auth.py                # Login y refresh JWT
│   └── migrations/
│
├── sucursales/                     # Sucursales de la cadena
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── asistencia/                    # Registro de marcajes
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── nomina/                        # Cálculo y consulta de nómina
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── reglas_laborales/              # Reglas por país y días festivos
│   ├── __init__.py
│   ├── regla_laboral.py
│   ├── dia_festivo.py
│   ├── models.py                  # Re-exporta los modelos
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
│
├── comprobantes/                  # Generación de comprobantes PDF
│   ├── services.py
│   └── views.py
│
├── solicitudes/                   # Vacaciones y permisos
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   └── migrations/
│
└── reportes/                      # Reportes y exportaciones
    └── views.py
```

Las carpetas `migrations/` ya están preparadas con su `__init__.py`; los
archivos de migración se generarán con `python manage.py makemigrations`.
La base de datos por defecto para desarrollo es SQLite; la configuración de
PostgreSQL se encuentra documentada en `database/README.md`.

## Roadmap sugerido

- [ ] Definir modelo de datos (usuarios, turnos, marcajes, nómina, sucursales)
- [ ] Implementar registro de asistencia
- [ ] Implementar motor de cálculo de nómina (horas extra, recargos)
- [ ] Implementar generación de comprobantes en PDF
- [ ] Implementar dashboard multi-sucursal
- [ ] Implementar módulo de reportes y auditoría
- [ ] Implementar módulo de vacaciones/permisos

---

*Este README describe el alcance funcional del proyecto. La arquitectura técnica (stack, base de datos, infraestructura) se definirá en una siguiente etapa.*