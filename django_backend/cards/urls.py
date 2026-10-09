from django.urls import path
from .views import CardListCreateView, CardDetailView

app_name = 'cards'

urlpatterns = [
    path('', CardListCreateView.as_view(), name='card-list-create'),
    path('<int:pk>/', CardDetailView.as_view(), name='card-detail'),
]
