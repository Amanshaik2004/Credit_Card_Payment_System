from django.db import models
from django.conf import settings

class Card(models.Model):
    CARD_TYPES = [
        ('CREDIT', 'Credit Card'),
        ('DEBIT', 'Debit Card'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    card_holder_name = models.CharField(max_length=100)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES, default='CREDIT')
    card_brand = models.CharField(max_length=30, default='Visa')
    masked_card_number = models.CharField(max_length=30)
    last_4_digits = models.CharField(max_length=4)
    expiry_month = models.PositiveSmallIntegerField()
    expiry_year = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'cards'
        db_table = 'cards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.card_brand} {self.masked_card_number} ({self.card_holder_name})"
