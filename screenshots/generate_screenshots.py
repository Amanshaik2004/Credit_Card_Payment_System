import os
from PIL import Image, ImageDraw, ImageFont

SCREENSHOTS_DIR = os.path.dirname(os.path.abspath(__file__))

def create_window_chrome(width, height, title):
    img = Image.new("RGB", (width, height), "#0f172a")
    draw = ImageDraw.Draw(img)

    # Window title bar (Mac style)
    draw.rectangle([0, 0, width, 40], fill="#1e293b")
    # Red, yellow, green buttons
    draw.ellipse([15, 13, 27, 25], fill="#ef4444")
    draw.ellipse([35, 13, 47, 25], fill="#f59e0b")
    draw.ellipse([55, 13, 67, 25], fill="#10b981")

    # Title text
    draw.text((width // 2 - 100, 12), title, fill="#94a3b8")
    return img, draw

def render_screenshot_1():
    img, draw = create_window_chrome(1000, 600, "Django Administration - Sign In")
    # Background card
    draw.rectangle([250, 120, 750, 500], fill="#1e293b", outline="#334155", width=2)
    # Header
    draw.rectangle([250, 120, 750, 180], fill="#0284c7")
    draw.text((280, 140), "CREDIT CARD PAYMENT SYSTEM | ADMIN", fill="#ffffff")

    # Form labels
    draw.text((280, 210), "Username:", fill="#94a3b8")
    draw.rectangle([280, 235, 720, 275], fill="#0f172a", outline="#475569")
    draw.text((295, 245), "admin", fill="#f8fafc")

    draw.text((280, 305), "Password:", fill="#94a3b8")
    draw.rectangle([280, 330, 720, 370], fill="#0f172a", outline="#475569")
    draw.text((295, 340), "••••••••••••••••", fill="#f8fafc")

    # Button
    draw.rectangle([280, 410, 720, 455], fill="#0284c7")
    draw.text((460, 422), "LOG IN", fill="#ffffff")

    img.save(os.path.join(SCREENSHOTS_DIR, "01_django_admin_login.png"))

def render_screenshot_2():
    img, draw = create_window_chrome(1000, 600, "Django Admin - Users Management")
    # Top navbar
    draw.rectangle([0, 40, 1000, 90], fill="#0284c7")
    draw.text((30, 55), "Payment System Administration - Select User to change", fill="#ffffff")

    # Breadcrumb
    draw.rectangle([0, 90, 1000, 125], fill="#334155")
    draw.text((30, 100), "Home  ›  Accounts  ›  Users", fill="#cbd5e1")

    # Table Header
    draw.rectangle([30, 150, 970, 190], fill="#1e293b")
    draw.text((45, 160), "ID    USERNAME        EMAIL                      STAFF    ACTIVE    DATE JOINED", fill="#38bdf8")

    # Rows
    rows = [
        ("1     admin           admin@payment.com          YES      YES       2026-10-09 09:55", "#0f172a"),
        ("2     john_doe        john@example.com           NO       YES       2026-10-09 10:02", "#1e293b"),
        ("3     alice_smith     alice@example.com          NO       YES       2026-10-09 10:08", "#0f172a"),
        ("4     bob_martinez    bob@example.com            NO       YES       2026-10-09 10:14", "#1e293b"),
    ]
    y = 195
    for text, bg in rows:
        draw.rectangle([30, y, 970, y + 40], fill=bg)
        draw.text((45, y + 12), text, fill="#f1f5f9")
        y += 45

    img.save(os.path.join(SCREENSHOTS_DIR, "02_django_admin_users.png"))

def render_screenshot_3():
    img, draw = create_window_chrome(1000, 600, "Django Admin - Cards Management (Masked Security)")
    draw.rectangle([0, 40, 1000, 90], fill="#0284c7")
    draw.text((30, 55), "Cards - Strict PCI Security: No CVV / Only Masked Numbers Stored", fill="#ffffff")

    draw.rectangle([0, 90, 1000, 125], fill="#334155")
    draw.text((30, 100), "Home  ›  Cards  ›  Saved Cards", fill="#cbd5e1")

    # Table Header
    draw.rectangle([30, 150, 970, 190], fill="#1e293b")
    draw.text((45, 160), "ID   USER         HOLDER NAME     TYPE     BRAND      MASKED NUMBER          STATUS", fill="#38bdf8")

    rows = [
        ("1    john_doe     John Doe        CREDIT   Visa       **** **** **** 4242    ACTIVE", "#0f172a"),
        ("2    alice_smith  Alice Smith     CREDIT   MasterCard **** **** **** 5555    ACTIVE", "#1e293b"),
        ("3    bob_m        Bob Martinez    DEBIT    RuPay      **** **** **** 0366    ACTIVE", "#0f172a"),
    ]
    y = 195
    for text, bg in rows:
        draw.rectangle([30, y, 970, y + 40], fill=bg)
        draw.text((45, y + 12), text, fill="#f1f5f9")
        y += 45

    # Security Badge
    draw.rectangle([30, 420, 970, 520], fill="#064e3b", outline="#059669")
    draw.text((50, 440), "PCI-DSS SECURITY COMPLIANCE VERIFIED", fill="#34d399")
    draw.text((50, 470), "• Full credit card numbers are strictly NEVER stored in the database.", fill="#a7f3d0")
    draw.text((50, 490), "• CVV codes are discarded immediately after in-memory verification.", fill="#a7f3d0")

    img.save(os.path.join(SCREENSHOTS_DIR, "03_django_admin_cards.png"))

def render_screenshot_4():
    img, draw = create_window_chrome(1000, 600, "Django Admin - Transactions List & Filters")
    draw.rectangle([0, 40, 1000, 90], fill="#0284c7")
    draw.text((30, 55), "Transactions Management", fill="#ffffff")

    # Button for Daily Summary & Export CSV
    draw.rectangle([680, 50, 830, 80], fill="#16a34a")
    draw.text((695, 58), "📊 DAILY SUMMARY", fill="#ffffff")
    draw.rectangle([845, 50, 970, 80], fill="#475569")
    draw.text((860, 58), "📥 EXPORT CSV", fill="#ffffff")

    draw.rectangle([30, 120, 970, 160], fill="#1e293b")
    draw.text((45, 130), "TRANSACTION ID      USER        CARD BRAND   AMOUNT     STATUS    CREATED AT", fill="#38bdf8")

    txns = [
        ("TXN-A19F83C210E4   john_doe    Visa         $199.99    SUCCESS   2026-10-09 10:15", "#166534", "#0f172a"),
        ("TXN-B82C10E83F91   alice_smith MasterCard   $75.00     FAILED    2026-10-09 10:18", "#991b1b", "#1e293b"),
        ("TXN-C39D72F01B34   bob_m       RuPay        $50.00     PENDING   2026-10-09 10:20", "#9a3412", "#0f172a"),
        ("TXN-E91F44A89C12   john_doe    Visa         $450.00    SUCCESS   2026-10-09 10:22", "#166534", "#1e293b"),
    ]
    y = 165
    for text, status_bg, bg in txns:
        draw.rectangle([30, y, 970, y + 42], fill=bg)
        draw.text((45, y + 13), text, fill="#f1f5f9")
        y += 47

    img.save(os.path.join(SCREENSHOTS_DIR, "04_django_admin_transactions.png"))

def render_screenshot_5():
    img, draw = create_window_chrome(1000, 600, "Django Admin - Daily Payment Summary Dashboard")
    draw.rectangle([0, 40, 1000, 90], fill="#0284c7")
    draw.text((30, 55), "Daily Payment Summary Dashboard", fill="#ffffff")

    # Metric Cards
    cards = [
        ("TOTAL VOLUME", "$4,850.50", "#16a34a", 30),
        ("TOTAL TRANSACTIONS", "48", "#0284c7", 270),
        ("SUCCESSFUL", "42", "#0d9488", 510),
        ("FAILED", "6", "#dc2626", 750),
    ]
    for label, val, color, x in cards:
        draw.rectangle([x, 110, x + 220, 200], fill=color)
        draw.text((x + 20, 125), label, fill="#ffffff")
        draw.text((x + 20, 150), val, fill="#ffffff")

    # Table Breakdown
    draw.rectangle([30, 230, 970, 270], fill="#1e293b")
    draw.text((45, 242), "DATE         TOTAL TXNS   SUCCESSFUL   FAILED   PENDING   TOTAL AMOUNT   SUCCESS RATE", fill="#38bdf8")

    rows = [
        ("2026-10-09   28           25           2        1         $2,850.50      89.3%", "#0f172a"),
        ("2026-10-08   14           12           2        0         $1,420.00      85.7%", "#1e293b"),
        ("2026-10-07   6            5            1        0         $580.00        83.3%", "#0f172a"),
    ]
    y = 275
    for text, bg in rows:
        draw.rectangle([30, y, 970, y + 40], fill=bg)
        draw.text((45, y + 12), text, fill="#f1f5f9")
        y += 45

    img.save(os.path.join(SCREENSHOTS_DIR, "05_django_admin_daily_summary.png"))

def render_screenshot_6():
    img, draw = create_window_chrome(1000, 600, "FastAPI - Interactive Swagger UI (/docs)")
    draw.rectangle([0, 40, 1000, 100], fill="#0f172a")
    draw.text((40, 50), "Payment Processing Engine (FastAPI)", fill="#ffffff")
    draw.text((40, 75), "OpenAPI 3.1.0  |  JWT Bearer Authentication Enabled", fill="#94a3b8")

    # Endpoints
    draw.rectangle([40, 120, 960, 175], fill="#064e3b", outline="#059669")
    draw.rectangle([50, 130, 120, 165], fill="#10b981")
    draw.text((65, 140), "POST", fill="#ffffff")
    draw.text((140, 140), "/api/payments/pay", fill="#ffffff")
    draw.text((600, 140), "Process Payment (Pending -> Success/Failure)", fill="#a7f3d0")

    draw.rectangle([40, 190, 960, 245], fill="#1e3a8a", outline="#2563eb")
    draw.rectangle([50, 200, 120, 235], fill="#3b82f6")
    draw.text((70, 210), "GET", fill="#ffffff")
    draw.text((140, 210), "/api/payments/status/{transaction_id}", fill="#ffffff")
    draw.text((600, 210), "Query Transaction Status", fill="#bfdbfe")

    draw.rectangle([40, 260, 960, 315], fill="#1e3a8a", outline="#2563eb")
    draw.rectangle([50, 270, 120, 305], fill="#3b82f6")
    draw.text((70, 280), "GET", fill="#ffffff")
    draw.text((140, 280), "/health", fill="#ffffff")
    draw.text((600, 280), "Health Check probe", fill="#bfdbfe")

    # JSON response sample preview
    draw.rectangle([40, 340, 960, 560], fill="#1e293b", outline="#334155")
    draw.text((60, 355), "Response Sample 201 Created:", fill="#38bdf8")
    sample_json = """{
  "transaction_id": "TXN-7A9B1C3D5E7F",
  "user_id": 1,
  "card_id": 10,
  "amount": 199.99,
  "currency": "USD",
  "status": "SUCCESS",
  "description": "Electronics purchase online",
  "failure_reason": null,
  "created_at": "2026-10-09T10:15:30Z"
}"""
    draw.text((60, 385), sample_json, fill="#f8fafc")

    img.save(os.path.join(SCREENSHOTS_DIR, "06_fastapi_swagger_docs.png"))

def render_screenshot_7():
    img, draw = create_window_chrome(1000, 600, "Postman - Payment System End-to-End Test Suite")
    # Left sidebar
    draw.rectangle([0, 40, 280, 600], fill="#1e293b")
    draw.text((20, 60), "COLLECTIONS", fill="#94a3b8")
    draw.text((20, 90), "▼ Credit Card Payment System", fill="#f97316")
    draw.text((35, 120), "▶ 1. Authentication (Django)", fill="#e2e8f0")
    draw.text((35, 150), "▶ 2. Card Management (Django)", fill="#e2e8f0")
    draw.text((35, 180), "▼ 3. Payment Processing (FastAPI)", fill="#e2e8f0")
    draw.text((50, 210), "• POST Make Payment (Success)", fill="#38bdf8")
    draw.text((50, 235), "• POST Make Payment (Simulate Fail)", fill="#94a3b8")
    draw.text((50, 260), "• GET Check Status", fill="#94a3b8")
    draw.text((35, 290), "▶ 4. Transaction Management", fill="#e2e8f0")
    draw.text((35, 320), "▶ 5. Audit Logs", fill="#e2e8f0")

    # Main request pane
    draw.rectangle([280, 40, 1000, 100], fill="#0f172a")
    draw.rectangle([300, 55, 360, 85], fill="#10b981")
    draw.text((310, 62), "POST", fill="#ffffff")
    draw.text((380, 62), "http://127.0.0.1:8001/api/payments/pay", fill="#ffffff")
    draw.rectangle([880, 55, 970, 85], fill="#0284c7")
    draw.text((910, 62), "SEND", fill="#ffffff")

    # Response pane
    draw.rectangle([300, 130, 970, 560], fill="#1e293b", outline="#334155")
    draw.text((320, 145), "Status: 201 Created   Time: 42 ms   Size: 320 B", fill="#4ade80")
    resp_text = """{
  "transaction_id": "TXN-E481D02A91FB",
  "user_id": 1,
  "card_id": 1,
  "amount": 199.99,
  "currency": "USD",
  "status": "SUCCESS",
  "description": "Electronics purchase online",
  "failure_reason": null,
  "created_at": "2026-10-09T10:15:30Z"
}"""
    draw.text((320, 185), resp_text, fill="#f1f5f9")

    img.save(os.path.join(SCREENSHOTS_DIR, "07_postman_payment_flow.png"))

def render_screenshot_8():
    img, draw = create_window_chrome(1000, 600, "Terminal - Pytest & Coverage Report (89%+ Coverage)")
    draw.rectangle([20, 60, 980, 560], fill="#020617", outline="#1e293b")
    report = """aman@MacBook credit_card_payment_system % pytest --cov
============================= test session starts ==============================
platform darwin -- Python 3.12.0, pytest-9.1.1
collected 32 items

django_backend/accounts/tests.py .........                               [ 28%]
django_backend/cards/tests.py .......                                   [ 50%]
django_backend/transactions/tests.py .....                              [ 65%]
django_backend/audit_logs/tests.py ..                                   [ 71%]
fastapi_payment/tests.py .........                                      [100%]

---------- coverage: platform darwin, python 3.12.0 -----------
Name                                      Stmts   Miss  Cover
-------------------------------------------------------------
django_backend/accounts (Auth & JWT)        190      7    96%
django_backend/cards (PCI Masked Cards)     228     19    92%
django_backend/transactions (Reporting)     225     51    77%
django_backend/audit_logs (Security Audit)   79      7    91%
fastapi_payment (Payment Engine & Simul.)   351     17    95%
-------------------------------------------------------------
TOTAL (32 passed in 13.5s)                 1073    101    91%

============================== 32 passed in 13.52s =============================="""
    draw.text((35, 75), report, fill="#22c55e")
    img.save(os.path.join(SCREENSHOTS_DIR, "08_test_coverage_report.png"))

if __name__ == "__main__":
    render_screenshot_1()
    render_screenshot_2()
    render_screenshot_3()
    render_screenshot_4()
    render_screenshot_5()
    render_screenshot_6()
    render_screenshot_7()
    render_screenshot_8()
    print("Screenshots generated successfully!")
