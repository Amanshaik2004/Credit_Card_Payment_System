import re
from datetime import datetime
from rest_framework import serializers
from .models import Card

def luhn_checksum_valid(card_number: str) -> bool:
    """Verifies card number using the standard Luhn algorithm."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            checksum += doubled if doubled < 10 else doubled - 9
        else:
            checksum += d
    return checksum % 10 == 0

def detect_card_brand(card_number: str) -> str:
    """Detects card brand from card number prefix."""
    if card_number.startswith('4'):
        return 'Visa'
    elif card_number.startswith(('51', '52', '53', '54', '55')) or (len(card_number) >= 4 and 2221 <= int(card_number[:4]) <= 2720):
        return 'MasterCard'
    elif card_number.startswith(('34', '37')):
        return 'American Express'
    elif card_number.startswith(('6011', '65')) or (len(card_number) >= 3 and 644 <= int(card_number[:3]) <= 649):
        return 'Discover'
    elif card_number.startswith(('60', '6521', '6522', '508')):
        return 'RuPay'
    return 'Other'

def format_masked_card(card_number: str) -> str:
    """Returns a cleanly formatted masked card string like **** **** **** 1234."""
    last4 = card_number[-4:]
    masked_part = "*" * (len(card_number) - 4)
    # Group in blocks of 4
    full_masked = masked_part + last4
    return " ".join([full_masked[i:i+4] for i in range(0, len(full_masked), 4)])


class CardCreateSerializer(serializers.ModelSerializer):
    # Sensitive fields are strictly write_only and are never saved to database
    card_number = serializers.CharField(write_only=True)
    cvv = serializers.CharField(write_only=True, min_length=3, max_length=4)

    class Meta:
        model = Card
        fields = [
            'id',
            'card_holder_name',
            'card_type',
            'card_number',
            'cvv',
            'expiry_month',
            'expiry_year',
            'card_brand',
            'masked_card_number',
            'last_4_digits',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'card_brand', 'masked_card_number', 'last_4_digits', 'is_active', 'created_at']

    def validate_card_number(self, value):
        cleaned = re.sub(r'[\s-]', '', value)
        if not cleaned.isdigit():
            raise serializers.ValidationError("Card number must contain only numeric digits.")
        if not (13 <= len(cleaned) <= 19):
            raise serializers.ValidationError("Card number length must be between 13 and 19 digits.")
        if not luhn_checksum_valid(cleaned):
            raise serializers.ValidationError("Invalid card number. Failed Luhn check verification.")
        return cleaned

    def validate_cvv(self, value):
        cleaned = value.strip()
        if not (cleaned.isdigit() and len(cleaned) in (3, 4)):
            raise serializers.ValidationError("CVV must be 3 or 4 numeric digits.")
        return cleaned

    def validate_expiry_month(self, value):
        if not (1 <= value <= 12):
            raise serializers.ValidationError("Expiry month must be between 1 and 12.")
        return value

    def validate(self, attrs):
        now = datetime.now()
        year = attrs.get('expiry_year')
        month = attrs.get('expiry_month')

        # Allow 2-digit year (e.g., 28 -> 2028)
        if year < 100:
            year += 2000
            attrs['expiry_year'] = year

        if year < now.year:
            raise serializers.ValidationError({"expiry_year": "Card has already expired."})
        elif year == now.year and month < now.month:
            raise serializers.ValidationError({"expiry_month": "Card has already expired."})

        return attrs

    def create(self, validated_data):
        # Extract sensitive values and DO NOT persist them
        raw_card_number = validated_data.pop('card_number')
        validated_data.pop('cvv')  # Discard CVV completely

        card_brand = detect_card_brand(raw_card_number)
        last_4_digits = raw_card_number[-4:]
        masked_card_number = format_masked_card(raw_card_number)

        # Assign user from context
        user = self.context['request'].user

        card = Card.objects.create(
            user=user,
            card_brand=card_brand,
            last_4_digits=last_4_digits,
            masked_card_number=masked_card_number,
            **validated_data
        )
        return card


class CardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            'id',
            'card_holder_name',
            'card_type',
            'card_brand',
            'masked_card_number',
            'last_4_digits',
            'expiry_month',
            'expiry_year',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields
