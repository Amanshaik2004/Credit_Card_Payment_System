from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from audit_logs.utils import record_audit_log
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    LogoutSerializer,
)

@extend_schema(tags=['Authentication'], summary='User Registration')
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens immediately
        refresh = RefreshToken.for_user(user)

        record_audit_log(
            action='USER_REGISTER',
            user=user,
            details=f"User {user.username} registered with email {user.email}",
            request=request
        )

        return Response({
            'message': 'User registered successfully.',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Authentication'], summary='User Login via JWT')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = data['user']

        record_audit_log(
            action='USER_LOGIN',
            user=user,
            details=f"User {user.username} logged in successfully",
            request=request
        )

        return Response({
            'message': 'Login successful.',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': data['access'],
                'refresh': data['refresh'],
            }
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'], summary='User Logout')
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        record_audit_log(
            action='USER_LOGOUT',
            user=request.user,
            details=f"User {request.user.username} logged out",
            request=request
        )

        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'], summary='User Profile (Protected Route)')
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
