from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from audit_logs.utils import record_audit_log
from .models import Card
from .serializers import CardCreateSerializer, CardListSerializer

@extend_schema(tags=['Cards'], summary='List user saved cards or Add new card')
class CardListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CardCreateSerializer
        return CardListSerializer

    def get_queryset(self):
        # Only return active cards belonging to the authenticated user
        return Card.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        card = serializer.save()
        record_audit_log(
            action='CARD_ADDED',
            user=self.request.user,
            details=f"Added {card.card_type} ({card.card_brand}) ending in {card.last_4_digits}",
            request=self.request
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'message': 'Card successfully added.',
            'card': CardListSerializer(serializer.instance).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Cards'], summary='Retrieve or Delete saved card')
class CardDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CardListSerializer

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user, is_active=True)

    def perform_destroy(self, instance):
        # Soft-delete by setting is_active=False
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        record_audit_log(
            action='CARD_DELETED',
            user=self.request.user,
            details=f"Deactivated {instance.card_brand} card ending in {instance.last_4_digits}",
            request=self.request
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Card deleted successfully.'}, status=status.HTTP_200_OK)
