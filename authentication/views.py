from datetime import date
from rest_framework import status
from rest_framework.decorators    import api_view, permission_classes
from rest_framework.permissions   import AllowAny
from rest_framework.response      import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models      import Dater
from .serializers import DaterRegistrationSerializer
from user_profile.models import Profile

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

    user_data = serializer.validated_data
    user_data.pop('password2')
    password = user_data.pop('password')
    user = Dater(**user_data)
    user.set_password(password)
    user.save()

    Profile.objects.create(user=user)

    refresh = RefreshToken.for_user(user)
    tokens  = {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }

    out_serializer = DaterRegistrationSerializer(user)
    return Response({
        "message": "Registration successful.",
        "user":    out_serializer.data,
        "tokens":  tokens,
    }, status=status.HTTP_201_CREATED)
