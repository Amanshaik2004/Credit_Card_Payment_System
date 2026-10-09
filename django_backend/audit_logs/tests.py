from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from audit_logs.models import AuditLog
from audit_logs.utils import record_audit_log

User = get_user_model()

class AuditLogTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse('audit_logs:audit-log-list')
        self.user = User.objects.create_user(username='dave', email='dave@example.com', password='Password123!')
        self.admin_user = User.objects.create_superuser(username='admin_dave', email='admin_dave@example.com', password='Password123!')

    def test_record_audit_log_utility(self):
        record_audit_log(action='TEST_ACTION', user=self.user, details='Test details')
        log = AuditLog.objects.filter(action='TEST_ACTION').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.details, 'Test details')

    def test_audit_log_list_admin_only(self):
        # Regular user -> 403 Forbidden
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # Admin -> 200 OK
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
