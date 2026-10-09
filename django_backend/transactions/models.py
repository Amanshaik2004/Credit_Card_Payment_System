import uuid
from django.db import models
from django.conf import settings

def generate_transaction_id():
    return f"TXN-{uuid.uuid4().hex[:12].upper()}"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    transaction_id = models.CharField(
        max_length=64,
        unique=True,
        default=generate_transaction_id,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    card = models.ForeignKey(
        'cards.Card',
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    description = models.CharField(max_length=255, blank=True, default='')
    failure_reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'transactions'
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['user']),
            models.Index(fields=['card']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.user.username} - {self.currency} {self.amount} ({self.status})"
