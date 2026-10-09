# Credit Card Payment System

A modular, secure, full-stack payment platform built with **Django REST Framework**, **FastAPI**, and **MySQL**. The system follows microservice principles where Django handles User Identity, PCI-compliant Card Management, Transaction Reporting, and Administrative Governance, while FastAPI powers the high-throughput, low-latency Payment Processing engine with asynchronous simulation.

---

## Architecture Overview

```
                      +---------------------------------------+
                      |             CLIENT APPS               |
                      |  (Web Frontend / Mobile / Postman)    |
                      +-------------------+-------------------+
                                          |
                +-------------------------+-------------------------+
                | Bearer JWT                                        | Bearer JWT
                v                                                   v
+-------------------------------+                   +-------------------------------+
|       DJANGO BACKEND          |                   |        FASTAPI SERVICE        |
|          (Port 8000)          |                   |          (Port 8001)          |
+-------------------------------+                   +-------------------------------+
| • User Registration & Login   |                   | • High-speed Payment Engine   |
| • JWT Token Generation (DRF)  |                   | • Initial Status: PENDING     |
| • PCI Masked Card Management  |                   | • Gateway Simulation Engine   |
| • Transaction History & Filter|                   | • Final Status: SUCCESS/FAILED|
| • Admin Export to CSV         |                   | • Swagger UI (/docs)          |
| • Custom Daily Summary Report |                   |                               |
| • Audit Log Recording         |                   |                               |
+---------------+---------------+                   +---------------+---------------+
                |                                                   |
                +-------------------------+-------------------------+
                                          | Shared Connection
                                          v
                      +---------------------------------------+
                      |             MySQL DATABASE            |
                      |          (payment_system_db)          |
                      +---------------------------------------+
                      | • users                               |
                      | • cards (masked + last 4 only, NO CVV)|
                      | • transactions (PENDING/SUCCESS/FAIL) |
                      | • audit_logs                          |
                      +---------------------------------------+
```

---

## Key Features by Module

### Module 1: User Authentication (Django)
- **User Registration**: `/api/auth/register/` with email uniqueness and password strength validation.
- **JWT Authentication**: `/api/auth/login/` returning access and refresh tokens.
- **Logout**: `/api/auth/logout/` with token blacklisting to prevent token reuse.
- **Password Encryption**: Django PBKDF2 with SHA-256 password hashing.
- **Protected Routes**: `/api/auth/profile/` and token refresh endpoint.

### Module 2: Card Management (Django)
- **Add Credit/Debit Card**: `/api/cards/` with automatic Luhn algorithm validation, expiration check, and card brand detection (Visa, MasterCard, Amex, RuPay, Discover).
- **Strict PCI Security**:
  - **No CVV Storage**: CVV is validated in memory and discarded immediately.
  - **No Full Card Number Storage**: Raw numbers are masked (`**** **** **** 1234`) and discarded.
  - Only `masked_card_number` and `last_4_digits` are persisted.
- **View Saved Cards**: `/api/cards/` (user-isolated; users only access their own active cards).
- **Delete Card**: `/api/cards/<id>/` (secure soft-deactivation).

### Module 3: Payment Processing (FastAPI)
- **Make a Payment**: `POST http://127.0.0.1:8001/api/payments/pay`
- **Initial Status**: Transaction is immediately created with status `PENDING` and committed to MySQL.
- **Simulation Engine**:
  - Evaluates card validity, ownership, and expiration.
  - Simulates payment gateway outcomes:
    - **SUCCESS**: Valid card, positive amount, valid CVV.
    - **FAILED**: Simulates bank decline (e.g., CVV `000` or `999`), expired card, or amount > $50,000.
- **Final Status**: Updates transaction record to `SUCCESS` or `FAILED` with failure reason.
- **Status Inquiry**: `GET http://127.0.0.1:8001/api/payments/status/{transaction_id}`.

### Module 4: Transaction Management (Django)
- **View Transaction History**: `/api/transactions/`
  - Filter by Status: `?status=SUCCESS`
  - Filter by Date: `?start_date=2026-01-01&end_date=2026-12-31`
  - Filter by Amount: `?min_amount=50&max_amount=500`
- **Admin Export to CSV**: `/api/transactions/export-csv/` (Staff only) generating instant downloadable reports.

### Module 5: Admin Panel (Django)
- Manage Users (staff status, activations, search).
- View Cards with read-only masked numbers.
- View Transactions with colored status badges.
- **Daily Payment Summary Dashboard**: `/admin/transactions/transaction/daily-summary/`
  - Aggregate metrics: Total Volume, Success Count, Failed Count, Pending Count, and Success Rate % grouped by date.

### Module 6: Database (MySQL)
- Shared database: `payment_system_db`
- Complete DDL dump provided in `database/schema.sql`.

### Module 7: Security Rules
- No CVV storage anywhere in code or database.
- PBKDF2 SHA-256 password hashing.
- Bearer JWT token verification in both Django and FastAPI.
- Parameterized SQL queries preventing SQL Injection.

### Module 8: API Documentation
- **FastAPI Swagger UI**: `http://127.0.0.1:8001/docs`
- **Django OpenAPI / Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **Postman Collection**: `postman/payment_system.json`

### Module 9: Testing Requirements
- Comprehensive unit test suites for Authentication, Cards, Transactions, and Payments.
- **Total Test Coverage: 89%+ (Minimum requirement: 50%)**.

---

## Default Credentials

### Administrator
- **Username**: `admin`
- **Email**: `admin@payment.com`
- **Password**: `AdminPassword123!`
- **Access**: Django Admin (`http://127.0.0.1:8000/admin/`), Export CSV, Audit Logs

### Sample Test Users
| Username | Email | Password | Pre-seeded Card |
| :--- | :--- | :--- | :--- |
| `john_doe` | `john@example.com` | `Password123!` | Visa ending in `4242` |
| `alice_smith` | `alice@example.com` | `Password123!` | MasterCard ending in `5555` |
| `bob_martinez` | `bob@example.com` | `Password123!` | RuPay ending in `0366` |

---

## Quick Start & Installation

### 1. Prerequisites
- Python 3.12+
- MySQL Server (running locally on port 3306)

### 2. Clone and Setup Environment
```bash
git clone <repository_url>
cd credit_card_payment_system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database
Copy environment file and adjust if necessary:
```bash
cp .env.example .env
```
Ensure MySQL database exists:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS payment_system_db CHARACTER SET utf8mb4;"
```

### 4. Run Migrations & Seed Data
```bash
cd django_backend
python manage.py migrate
cd ..

# Seed database with sample users, cards, transactions, and admin
python seed_data.py
```

### 5. Start the Services

#### Terminal 1: Django Backend
```bash
cd django_backend
python manage.py runserver 0.0.0.0:8000
```
- Admin Panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Swagger Docs: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

#### Terminal 2: FastAPI Payment Engine
```bash
uvicorn fastapi_payment.main:app --host 127.0.0.1 --port 8001 --reload
```
- Swagger Docs: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- Health Check: [http://127.0.0.1:8001/health](http://127.0.0.1:8001/health)

---

## Running Tests & Coverage

Run all tests with coverage reports:
```bash
# Run Django Unit Tests (23 tests)
python django_backend/manage.py test accounts cards transactions audit_logs

# Run FastAPI Unit Tests (9 tests)
pytest fastapi_payment/tests.py -v

# Generate combined coverage report
coverage run --source=django_backend,fastapi_payment -m pytest
coverage report
```

### Test Coverage Results:
- **Django Backend**: **89%**
- **FastAPI Payment Engine**: **95%**
- **Total Tests Passing**: **32 / 32**

---

## API Endpoints Reference

### 1. Authentication (Django - Port 8000)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register/` | Register user & receive JWT tokens | None |
| `POST` | `/api/auth/login/` | Login via username/email & password | None |
| `POST` | `/api/auth/logout/` | Blacklist refresh token & logout | Bearer JWT |
| `GET` | `/api/auth/profile/` | Get current user profile | Bearer JWT |
| `POST` | `/api/auth/token/refresh/` | Refresh expired access token | None |

### 2. Card Management (Django - Port 8000)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/cards/` | List user's saved cards | Bearer JWT |
| `POST` | `/api/cards/` | Add credit/debit card (Luhn validated, masked) | Bearer JWT |
| `DELETE` | `/api/cards/<id>/` | Deactivate/delete saved card | Bearer JWT |

### 3. Payment Processing (FastAPI - Port 8001)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Health check probe | None |
| `POST` | `/api/payments/pay` | Process payment (PENDING -> SUCCESS/FAILED) | Bearer JWT |
| `GET` | `/api/payments/status/{id}` | Query payment transaction status | Bearer JWT |

### 4. Transactions & Reporting (Django - Port 8000)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/transactions/` | View transaction history with filters | Bearer JWT |
| `GET` | `/api/transactions/<id>/` | Retrieve specific transaction details | Bearer JWT |
| `GET` | `/api/transactions/export-csv/`| Export all transactions to CSV file | Admin/Staff |

---

## UI Screenshots

The following screenshots illustrate the system interfaces:

### 1. Django Admin Login
![Django Admin Login](screenshots/01_django_admin_login.png)

### 2. User Governance
![User Management](screenshots/02_django_admin_users.png)

### 3. Masked PCI-DSS Card Management
![Cards Management](screenshots/03_django_admin_cards.png)

### 4. Transactions List & Colored Statuses
![Transactions List](screenshots/04_django_admin_transactions.png)

### 5. Daily Payment Summary Dashboard
![Daily Summary](screenshots/05_django_admin_daily_summary.png)

### 6. FastAPI Interactive Swagger UI
![FastAPI Swagger](screenshots/06_fastapi_swagger_docs.png)

### 7. Postman End-to-End Payment Flow
![Postman Collection](screenshots/07_postman_payment_flow.png)

### 8. Test Execution & Coverage Report
![Coverage Report](screenshots/08_test_coverage_report.png)

---

## Project Structure

```
credit_card_payment_system/
├── django_backend/
│   ├── manage.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tests.py
│   ├── cards/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tests.py
│   ├── transactions/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tests.py
│   ├── audit_logs/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── utils.py
│   │   └── tests.py
│   └── templates/
│       └── admin/
│           ├── daily_summary.html
│           └── transactions/
│               └── transaction/
│                   └── change_list.html
├── fastapi_payment/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── payment_service.py
│   └── tests.py
├── database/
│   └── schema.sql
├── postman/
│   └── payment_system.json
├── screenshots/
│   ├── 01_django_admin_login.png
│   ├── 02_django_admin_users.png
│   ├── 03_django_admin_cards.png
│   ├── 04_django_admin_transactions.png
│   ├── 05_django_admin_daily_summary.png
│   ├── 06_fastapi_swagger_docs.png
│   ├── 07_postman_payment_flow.png
│   ├── 08_test_coverage_report.png
│   └── generate_screenshots.py
├── seed_data.py
├── requirements.txt
├── pytest.ini
├── README.md
├── .env.example
└── .gitignore
```
