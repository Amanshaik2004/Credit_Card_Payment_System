from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Card

User = get_user_model()

class CardManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cards_url = reverse('cards:card-list-create')

        # Create two test users
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='Password123!'
        )

        # Authenticate user1 by default
        self.client.force_authenticate(user=self.user1)

        # Standard test card (valid Luhn format)
        self.valid_card_data = {
            'card_holder_name': 'Alice Smith',
            'card_type': 'CREDIT',
            'card_number': '4532015112830366',  # Valid Visa Luhn card
            'cvv': '123',
            'expiry_month': 12,
            'expiry_year': 2029
        }

    def test_add_card_success(self):
        response = self.client.post(self.cards_url, self.valid_card_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('card', response.data)
        card_data = response.data['card']

        self.assertEqual(card_data['card_holder_name'], 'Alice Smith')
        self.assertEqual(card_data['last_4_digits'], '0366')
        self.assertEqual(card_data['card_brand'], 'Visa')

        # SECURITY RULE CHECK: Ensure no CVV or full card number is stored in DB
        card = Card.objects.get(id=card_data['id'])
        self.assertEqual(card.last_4_digits, '0366')
        self.assertTrue(card.masked_card_number.endswith('0366'))
        self.assertTrue('****' in card.masked_card_number)

        # Inspect model fields: verify card_number and cvv fields do NOT even exist on the model
        model_field_names = [f.name for f in Card._meta.get_fields()]
        self.assertNotIn('card_number', model_field_names)
        self.assertNotIn('cvv', model_field_names)

    def test_add_card_invalid_luhn(self):
        invalid_data = self.valid_card_data.copy()
        invalid_data['card_number'] = '4532015112830367'  # Invalid checksum digit
        response = self.client.post(self.cards_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('card_number', response.data)

    def test_add_card_invalid_cvv(self):
        invalid_data = self.valid_card_data.copy()
        invalid_data['cvv'] = '12'  # Too short
        response = self.client.post(self.cards_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_expired_card(self):
        expired_data = self.valid_card_data.copy()
        expired_data['expiry_year'] = 2020  # Past year
        response = self.client.post(self.cards_url, expired_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_saved_cards(self):
        # Create card for user1
        self.client.post(self.cards_url, self.valid_card_data, format='json')

        response = self.client.get(self.cards_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated or list response
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['last_4_digits'], '0366')

    def test_user_card_isolation(self):
        # Alice creates a card
        self.client.post(self.cards_url, self.valid_card_data, format='json')

        # Bob logs in and checks cards
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.cards_url)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 0)

    def test_delete_card(self):
        create_resp = self.client.post(self.cards_url, self.valid_card_data, format='json')
        card_id = create_resp.data['card']['id']

        detail_url = reverse('cards:card-detail', kwargs={'pk': card_id})
        delete_resp = self.client.delete(detail_url)
        self.assertEqual(delete_resp.status_code, status.HTTP_200_OK)

        # Verify card is deactivated
        card = Card.objects.get(id=card_id)
        self.assertFalse(card.is_active)

        # Should not appear in active cards list
        list_resp = self.client.get(self.cards_url)
        results = list_resp.data.get('results', list_resp.data)
        self.assertEqual(len(results), 0)
