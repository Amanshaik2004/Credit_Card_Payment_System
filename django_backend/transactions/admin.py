from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.utils.html import format_html
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'user_link',
        'card_info',
        'formatted_amount',
        'colored_status',
        'created_at'
    )
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'user__email', 'card__last_4_digits')
    readonly_fields = (
        'transaction_id',
        'user',
        'card',
        'amount',
        'currency',
        'status',
        'description',
        'failure_reason',
        'created_at',
        'updated_at'
    )

    def user_link(self, obj):
        return f"{obj.user.username} ({obj.user.email})"
    user_link.short_description = "User"

    def card_info(self, obj):
        if obj.card:
            return f"{obj.card.card_brand} {obj.card.masked_card_number}"
        return "N/A"
    card_info.short_description = "Card"

    def formatted_amount(self, obj):
        return f"{obj.currency} {obj.amount:.2f}"
    formatted_amount.short_description = "Amount"

    def colored_status(self, obj):
        colors = {
            'SUCCESS': '#28a745',
            'FAILED': '#dc3545',
            'PENDING': '#e67e22',
        }
        color = colors.get(obj.status, '#333')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.status
        )
    colored_status.short_description = "Status"

    def has_add_permission(self, request):
        # Transactions are generated programmatically via payment gateway
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('daily-summary/', self.admin_site.admin_view(self.daily_summary_view), name='daily-payment-summary'),
        ]
        return custom_urls + urls

    def daily_summary_view(self, request):
        """Admin View for Daily Payment Summary (MODULE 5)."""
        daily_stats = (
            Transaction.objects
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(
                total_count=Count('id'),
                success_count=Count('id', filter=Q(status='SUCCESS')),
                failed_count=Count('id', filter=Q(status='FAILED')),
                pending_count=Count('id', filter=Q(status='PENDING')),
                total_amount=Sum('amount', filter=Q(status='SUCCESS')),
            )
            .order_by('-date')
        )

        daily_rows = []
        overall_total = 0
        overall_success = 0
        overall_failed = 0
        overall_pending = 0
        total_success_volume = 0.0

        for item in daily_stats:
            tot = item['total_count']
            suc = item['success_count']
            fld = item['failed_count']
            pnd = item['pending_count']
            amt = float(item['total_amount'] or 0.0)

            rate = (suc / tot * 100.0) if tot > 0 else 0.0

            daily_rows.append({
                'date': item['date'].strftime('%Y-%m-%d') if item['date'] else 'Unknown',
                'total_count': tot,
                'success_count': suc,
                'failed_count': fld,
                'pending_count': pnd,
                'total_amount': amt,
                'success_rate': rate,
            })

            overall_total += tot
            overall_success += suc
            overall_failed += fld
            overall_pending += pnd
            total_success_volume += amt

        context = dict(
            self.admin_site.each_context(request),
            title="Daily Payment Summary",
            daily_rows=daily_rows,
            overall_total_count=overall_total,
            overall_success_count=overall_success,
            overall_failed_count=overall_failed,
            overall_pending_count=overall_pending,
            total_success_volume=total_success_volume,
        )
        return TemplateResponse(request, "admin/daily_summary.html", context)
