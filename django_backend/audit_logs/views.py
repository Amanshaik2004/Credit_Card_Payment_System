from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema
from .models import AuditLog
from .serializers import AuditLogSerializer

@extend_schema(tags=['Audit Logs'], summary='List audit logs (Staff/Admin only)')
class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = AuditLog.objects.all().select_related('user')
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action__icontains=action)
        return queryset
