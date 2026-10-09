from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from cards.models import Card
from transactions.models import Transaction

User = get_user_model()

class TransactionManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.transactions_url = reverse('transactions:transaction-list')
        self.export_csv_url = reverse('transactions:transaction-export-csv')

        self.user = User.objects.create_user(
            username='charlie',
            email='charlie@example.com',
            password='Password123!'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin_charlie',
            email='admin_charlie@example.com',
            password='Password123!'
        )

        self.card = Card.objects.create(
            user=self.user,
            card_holder_name='Charlie Brown',
            card_type='CREDIT',
            card_brand='Visa',
            masked_card_number='**** **** **** 1111',
            last_4_digits='1111',
            expiry_month=11,
            expiry_year=2028
        )

        # Create sample transactions
        self.txn1 = Transaction.objects.create(
            transaction_id='TXN-TEST-001',
            user=self.user,
            card=self.card,
            amount=Decimal('100.00'),
            currency='USD',
            status='SUCCESS',
            description='Test payment 1'
        )
        self.txn2 = Transaction.objects.create(
            transaction_id='TXN-TEST-002',
            user=self.user,
            card=self.card,
            amount=Decimal('250.00'),
            currency='USD',
            status='FAILED',
            description='Test payment 2',
            failure_reason='Card declined'
        )
        self.txn3 = Transaction.objects.create(
            transaction_id='TXN-TEST-003',
            user=self.user,
            card=self.card,
            amount=Decimal('50.00'),
            currency='USD',
            status='PENDING',
            description='Test payment 3'
        )

    def test_view_transaction_history(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.transactions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 3)

    def test_filter_by_status(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.transactions_url}?status=SUCCESS")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['transaction_id'], 'TXN-TEST-001')

    def test_filter_by_amount(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.transactions_url}?min_amount=150&max_amount=300")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['transaction_id'], 'TXN-TEST-002')

    def test_admin_export_csv_forbidden_for_regular_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.export_csv_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_export_csv_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.export_csv_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="transactions_', response['Content-Disposition'])

        content = response.content.decode('utf-8')
        self.assertIn('Transaction ID', content)
        self.assertIn('TXN-TEST-001', content)
        self.assertIn('TXN-TEST-002', content)
