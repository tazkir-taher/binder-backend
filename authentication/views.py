# authentication/views.py

from datetime import date
import random

from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from user_profile.models import Profile
from .serializers import DaterRegistrationSerializer

User = get_user_model()


def _generate_unique_username(first_name: str, last_name: str) -> str:
    base = f"{first_name}{last_name}".lower()
    for _ in range(5):
        suffix = str(random.randint(1000, 9999))
        candidate = base + suffix
        if not User.objects.filter(username=candidate).exists():
            return candidate

    return base + date.today().strftime("%Y%m%d%H%M%S")


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    pw, pw2 = data.get('password'), data.get('password2')
    if not pw or not pw2:
        return Response({"detail": "Both password and password2 are required."},
                        status=status.HTTP_400_BAD_REQUEST)
    if pw != pw2:
        return Response({"password2": "Passwords do not match."},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = DaterRegistrationSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    birth = serializer.validated_data.get('birth_date')
    if birth:
        today = date.today()
        years = today.year - birth.year
        had_bday = (today.month, today.day) >= (birth.month, birth.day)
        age = years if had_bday else years - 1
        if age < 18:
            return Response({"detail": "You must be at least 18 years old to register."},
                            status=status.HTTP_400_BAD_REQUEST)

    user_data = serializer.validated_data.copy()
    user_data.pop('password2')
    password = user_data.pop('password')

    username = _generate_unique_username(user_data['first_name'], user_data['last_name'])

    try:
        user = User(username=username, **user_data)
        user.set_password(password)
        user.save()
    except IntegrityError:
        return Response({"detail": "Error creating user. Please try again."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    Profile.objects.create(user=user)

    refresh = RefreshToken.for_user(user)
    tokens = {'refresh': str(refresh), 'access': str(refresh.access_token)}

    return Response({
        "message": "Registration successful.",
        "user": {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "birth_date": str(user.birth_date),
            "gender": user.gender,
            "age": user.age,
        },
        "tokens": tokens,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email, password = request.data.get('email'), request.data.get('password')
    if not email or not password:
        return Response({"detail": "Email and password are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"detail": "Invalid credentials."},
                        status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({"detail": "Invalid credentials."},
                        status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "Login successful.",
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"detail": "Refresh token is required."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"detail": "Invalid or expired token."},
                        status=status.HTTP_400_BAD_REQUEST)
