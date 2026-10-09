import os
import sys
from decimal import Decimal
from datetime import datetime, timedelta, timezone

# Add django_backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'django_backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from cards.models import Card
from transactions.models import Transaction
from audit_logs.utils import record_audit_log

User = get_user_model()

def seed():
    print("Seeding database...")

    # 1. Superuser
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@payment.com',
            'first_name': 'System',
            'last_name': 'Administrator',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('AdminPassword123!')
        admin.save()
        print("Created admin superuser: admin / AdminPassword123!")
    else:
        print("Admin user already exists.")

    # 2. Regular Test Users
    user1, _ = User.objects.get_or_create(
        username='john_doe',
        defaults={
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
        }
    )
    user1.set_password('Password123!')
    user1.save()

    user2, _ = User.objects.get_or_create(
        username='alice_smith',
        defaults={
            'email': 'alice@example.com',
            'first_name': 'Alice',
            'last_name': 'Smith',
        }
    )
    user2.set_password('Password123!')
    user2.save()

    user3, _ = User.objects.get_or_create(
        username='bob_martinez',
        defaults={
            'email': 'bob@example.com',
            'first_name': 'Bob',
            'last_name': 'Martinez',
        }
    )
    user3.set_password('Password123!')
    user3.save()

    # 3. Cards (PCI compliant: only masked number and last 4 digits)
    card1, _ = Card.objects.get_or_create(
        user=user1,
        last_4_digits='4242',
        defaults={
            'card_holder_name': 'John Doe',
            'card_type': 'CREDIT',
            'card_brand': 'Visa',
            'masked_card_number': '**** **** **** 4242',
            'expiry_month': 12,
            'expiry_year': 2029,
            'is_active': True,
        }
    )

    card2, _ = Card.objects.get_or_create(
        user=user2,
        last_4_digits='5555',
        defaults={
            'card_holder_name': 'Alice Smith',
            'card_type': 'CREDIT',
            'card_brand': 'MasterCard',
            'masked_card_number': '**** **** **** 5555',
            'expiry_month': 8,
            'expiry_year': 2028,
            'is_active': True,
        }
    )

    card3, _ = Card.objects.get_or_create(
        user=user3,
        last_4_digits='0366',
        defaults={
            'card_holder_name': 'Bob Martinez',
            'card_type': 'DEBIT',
            'card_brand': 'RuPay',
            'masked_card_number': '**** **** **** 0366',
            'expiry_month': 5,
            'expiry_year': 2030,
            'is_active': True,
        }
    )

    # 4. Transactions
    sample_txns = [
        ('TXN-8A19F83C210E', user1, card1, Decimal('199.99'), 'USD', 'SUCCESS', 'Online shopping at Amazon', None, 0),
        ('TXN-9B82C10E83F9', user2, card2, Decimal('75.50'), 'USD', 'SUCCESS', 'Grocery store purchase', None, 0),
        ('TXN-AC39D72F01B3', user3, card3, Decimal('45.00'), 'USD', 'FAILED', 'Streaming subscription renewal', 'CVV check failed / Declined by issuing bank', 0),
        ('TXN-BE91F44A89C1', user1, card1, Decimal('320.00'), 'USD', 'SUCCESS', 'Airline ticket booking', None, 1),
        ('TXN-CF02A55B90D2', user2, card2, Decimal('12.99'), 'USD', 'SUCCESS', 'Coffee shop payment', None, 1),
        ('TXN-DA13B66C01E3', user3, card3, Decimal('55000.00'), 'USD', 'FAILED', 'Luxury watch purchase', 'Transaction amount exceeds per-transaction limit', 1),
        ('TXN-EB24C77D12F4', user1, card1, Decimal('88.40'), 'USD', 'PENDING', 'Pending hotel reservation authorization', None, 2),
    ]

    for txn_id, u, c, amt, curr, st, desc, fail_reason, days_ago in sample_txns:
        txn, created = Transaction.objects.get_or_create(
            transaction_id=txn_id,
            defaults={
                'user': u,
                'card': c,
                'amount': amt,
                'currency': curr,
                'status': st,
                'description': desc,
                'failure_reason': fail_reason,
            }
        )
        if created and days_ago > 0:
            created_time = datetime.now(timezone.utc) - timedelta(days=days_ago)
            Transaction.objects.filter(pk=txn.pk).update(created_at=created_time, updated_at=created_time)

    # 5. Audit Logs
    record_audit_log('SYSTEM_SEED', user=admin, details='Database seeded with sample users, cards, and transactions')
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()
