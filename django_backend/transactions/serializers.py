from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    card_brand = serializers.CharField(source='card.card_brand', read_only=True)
    card_masked = serializers.CharField(source='card.masked_card_number', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_id',
            'user',
            'username',
            'card',
            'card_brand',
            'card_masked',
            'amount',
            'currency',
            'status',
            'description',
            'failure_reason',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields
