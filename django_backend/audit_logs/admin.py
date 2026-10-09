from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'user', 'action', 'ip_address')
    list_filter = ('action', 'created_at')
    search_fields = ('action', 'user__username', 'ip_address', 'details')
    readonly_fields = ('user', 'action', 'ip_address', 'details', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
