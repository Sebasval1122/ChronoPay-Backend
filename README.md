# ChronoPay Backend

ChronoPay is a Django and Django REST Framework backend for multi-branch businesses. It records employee attendance and uses those records to calculate payroll, overtime, surcharges, deductions, and benefits according to the labor rules configured for each country.

## Features

### Payroll and compensation

- Automatic separation of regular and overtime hours into daytime and nighttime periods.
- Automatic Sunday and public-holiday surcharges.
- PDF pay-slip generation with worked hours, surcharges, deductions, and net pay.
- Salary-change history for every employee, available through the API.

### Multi-company administration

- Public company registration creates the company, its first branch, and its first administrator.
- Role-based access for general administrators, branch managers, and employees.
- Country-specific labor-rule configuration for overtime, surcharges, and benefits.

### Reports and time-off requests

- CSV payroll reports filtered according to the requesting user's role.
- Vacation and permission requests with manager or administrator approval workflows.

## Roles

### General administrator

Manages the entire company group, including branches, users, labor rules, salary history, reports, and time-off requests.

### Branch manager

Manages attendance, payroll, pay slips, salary history, reports, and time-off requests for the manager's own branch.

### Employee

Records clock-in and clock-out events, reviews attendance and payroll information, downloads personal pay slips, reviews salary history, and submits vacation or permission requests.

## Project structure

```text
payroll_attendance/
├── manage.py
├── requirements.txt
├── config/                 # Global Django configuration
├── database/               # SQLite and PostgreSQL configuration examples
├── common/                 # Shared permissions and utilities
├── companies/              # Company registration and tenant administration
├── users/                  # Users, roles, and authentication
├── branches/               # Company branches
├── attendance/             # Clock-in and clock-out records
├── payroll/                # Payroll calculation and DIAN integration
├── labor_rules/            # Country-specific labor rules and holidays
├── work_events/            # Sick leave, leave, and permission records
├── privacy/                # Data policies and consent
├── pay_slips/              # PDF pay-slip generation
├── time_off_requests/               # Vacation and permission requests
└── reports/                # Exportable CSV reports
```

## Development

The default development database is SQLite. PostgreSQL configuration is documented in `payroll_attendance/database/README.md`.

Set `SECRET_KEY` before running Django commands, then use:

```powershell
cd payroll_attendance
python manage.py check
python manage.py test
```

## Roadmap

- [x] Attendance registration
- [x] Payroll calculation with overtime and surcharges
- [x] PDF pay-slip generation
- [x] Vacation and permission API
- [x] Secure public multi-company registration
- [ ] Frontend screens for time-off requests, salary history, and CSV reports
- [ ] Consolidated multi-branch dashboard
- [ ] Projected versus actual payroll-cost dashboard
- [ ] Notifications
- [ ] Production digital signature for electronic payroll documents
- [ ] UVT-based withholding table
- [ ] Email and CAPTCHA verification for public registration
- [ ] Billing and subscription plans

The README describes the current backend scope. Production hosting, HTTPS, and managed database decisions will be defined in a later stage.
