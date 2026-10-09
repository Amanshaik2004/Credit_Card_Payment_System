from django.contrib import admin
from .models import Card

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'card_holder_name', 'card_type', 'card_brand', 'masked_card_number', 'is_active', 'created_at')
    list_filter = ('card_type', 'card_brand', 'is_active', 'created_at')
    search_fields = ('card_holder_name', 'last_4_digits', 'user__username', 'user__email')
    readonly_fields = ('masked_card_number', 'last_4_digits', 'created_at', 'updated_at')

    def has_add_permission(self, request):
        # Adding cards with raw numbers should only happen via secure API endpoints
        return False
