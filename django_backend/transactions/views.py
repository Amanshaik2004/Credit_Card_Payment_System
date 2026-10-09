import csv
from datetime import datetime
from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from audit_logs.utils import record_audit_log
from .models import Transaction
from .serializers import TransactionSerializer

@extend_schema(
    tags=['Transactions'],
    summary='List Transaction History with filters',
    parameters=[
        OpenApiParameter('status', str, description='Filter by status: PENDING, SUCCESS, FAILED'),
        OpenApiParameter('start_date', str, description='Filter transactions from YYYY-MM-DD'),
        OpenApiParameter('end_date', str, description='Filter transactions to YYYY-MM-DD'),
        OpenApiParameter('min_amount', float, description='Minimum transaction amount'),
        OpenApiParameter('max_amount', float, description='Maximum transaction amount'),
    ]
)
class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Staff can view all transactions; regular users only view their own
        if user.is_staff:
            queryset = Transaction.objects.all().select_related('user', 'card')
        else:
            queryset = Transaction.objects.filter(user=user).select_related('user', 'card')

        # Filter by Status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status__iexact=status_param.strip())

        # Filter by Date
        start_date = self.request.query_params.get('start_date')
        if start_date:
            try:
                dt_start = datetime.strptime(start_date.strip(), '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=dt_start)
            except ValueError:
                pass

        end_date = self.request.query_params.get('end_date')
        if end_date:
            try:
                dt_end = datetime.strptime(end_date.strip(), '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(created_at__lte=dt_end)
            except ValueError:
                pass

        # Filter by Amount
        min_amount = self.request.query_params.get('min_amount')
        if min_amount:
            try:
                queryset = queryset.filter(amount__gte=float(min_amount))
            except ValueError:
                pass

        max_amount = self.request.query_params.get('max_amount')
        if max_amount:
            try:
                queryset = queryset.filter(amount__lte=float(max_amount))
            except ValueError:
                pass

        return queryset


@extend_schema(tags=['Transactions'], summary='Retrieve transaction details')
class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all().select_related('user', 'card')
        return Transaction.objects.filter(user=self.request.user).select_related('user', 'card')


@extend_schema(
    tags=['Transactions'],
    summary='Admin Export to CSV (Staff only)',
    responses={(200, 'text/csv'): bytes}
)
class ExportTransactionsCSVView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="transactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Transaction ID',
            'Username',
            'User Email',
            'Card Brand',
            'Masked Card',
            'Amount',
            'Currency',
            'Status',
            'Description',
            'Failure Reason',
            'Date Created'
        ])

        transactions = Transaction.objects.all().select_related('user', 'card').order_by('-created_at')
        count = 0
        for txn in transactions:
            writer.writerow([
                txn.transaction_id,
                txn.user.username,
                txn.user.email,
                txn.card.card_brand if txn.card else 'N/A',
                txn.card.masked_card_number if txn.card else 'N/A',
                txn.amount,
                txn.currency,
                txn.status,
                txn.description,
                txn.failure_reason or '',
                txn.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
            count += 1

        record_audit_log(
            action='TRANSACTION_EXPORTED',
            user=request.user,
            details=f"Admin {request.user.username} exported {count} transactions to CSV",
            request=request
        )

        return response
