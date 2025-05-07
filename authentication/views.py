import random
from datetime import date
from django.db import IntegrityError
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Dater
from .serializers import DaterRegistrationSerializer
from user_profile.models import Profile

def _generate_unique_username(first_name: str, last_name: str) -> str:
    base = f"{first_name}{last_name}".lower()
    for _ in range(5):
        suffix = str(random.randint(1000, 9999))
        uname = base + suffix
        if not Dater.objects.filter(username=uname).exists():
            return uname
    # fallback in unlikely event of collision
    return base + str(date.today().strftime("%Y%m%d%H%M%S"))

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    pw  = data.get('password')
    pw2 = data.get('password2')
    if not pw or not pw2:
        return Response(
            {"detail": "Both password and password2 are required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    if pw != pw2:
        return Response(
            {"password2": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = DaterRegistrationSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # age check
    birth = serializer.validated_data.get('birth_date')
    if birth:
        today = date.today()
        years = today.year - birth.year
        had_bday = (today.month, today.day) >= (birth.month, birth.day)
        age = years if had_bday else years - 1
        if age < 18:
            return Response(
                {"detail": "You must be at least 18 years old to register."},
                status=status.HTTP_400_BAD_REQUEST
            )

    user_data = serializer.validated_data.copy()
    user_data.pop('password2')
    password = user_data.pop('password')

    # auto-generate a username
    uname = _generate_unique_username(
        user_data['first_name'],
        user_data['last_name']
    )

    # build and save user
    try:
        user = Dater(username=uname, **user_data)
        user.set_password(password)
        user.save()
    except IntegrityError:
        return Response(
            {"detail": "Could not generate a unique username, try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    Profile.objects.create(user=user)
    refresh = RefreshToken.for_user(user)
    tokens  = {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }

    out = {
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
    }
    return Response(out, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    tokens = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    return Response({
        "message": "Login successful.",
        "tokens": tokens
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {"message": "Logout successful."}, 
            status=status.HTTP_205_RESET_CONTENT
        )
    except Exception as e:
        return Response(
            {"detail": "Invalid token or already blacklisted."},
            status=status.HTTP_400_BAD_REQUEST
        )