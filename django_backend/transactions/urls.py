from django.urls import path
from .views import TransactionListView, TransactionDetailView, ExportTransactionsCSVView

app_name = 'transactions'

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('export-csv/', ExportTransactionsCSVView.as_view(), name='transaction-export-csv'),
]
