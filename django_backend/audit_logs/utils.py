import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def record_audit_log(action: str, user=None, details=None, request=None):
    from .models import AuditLog
    try:
        ip = get_client_ip(request) if request else None
        AuditLog.objects.create(
            user=user if (user and user.is_authenticated) else None,
            action=action,
            ip_address=ip,
            details=str(details) if details else None
        )
    except Exception as exc:
        logger.error(f"Failed to write audit log: {exc}")
