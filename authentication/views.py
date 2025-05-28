import base64, mimetypes
from datetime import date
from django.http import FileResponse, Http404
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import *

User = get_user_model()

def _compute_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    years = today.year - birth_date.year
    had_bday = (today.month, today.day) >= (birth_date.month, birth_date.day)
    return years if had_bday else years - 1

def _compute_like_count(user):
    return user.received_connections.filter(matched=False).count()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    pw, pw2 = data.get('password'), data.get('password2')

    if not pw or not pw2:
        return Response({
            "message": "Both password fields are required.",
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        })
    if pw != pw2:
        return Response({
            "message": "Passwords do not match.",
            "code": status.HTTP_400_BAD_REQUEST
        })

    serializer = DaterRegistrationSerializer(data=data)
    if not serializer.is_valid():
        return Response({
            "message": "Validation errors.",
            "code": status.HTTP_400_BAD_REQUEST,
            "data": serializer.errors
        })

    birth = serializer.validated_data.get('birth_date')
    if birth:
        today = date.today()
        years = today.year - birth.year
        had_bday = (today.month, today.day) >= (birth.month, birth.day)
        age = years if had_bday else years - 1
        if age < 18:
            return Response({
                "message": "You must be at least 18 to register.",
                "code": status.HTTP_400_BAD_REQUEST
            })

    user_data = serializer.validated_data.copy()
    user_data.pop('password2')
    raw_password = user_data.pop('password')

    try:
        user = User(**user_data)
        user.set_password(raw_password)
        user.save()
    except IntegrityError as e:
        return Response({
            "message": f"Error creating user: {e}",
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "data": {}
        })

    refresh = RefreshToken.for_user(user)
    tokens = {'refresh': str(refresh), 'access': str(refresh.access_token)}

    user_data = DaterSerializer(user, context={'request': request}).data
    user_data = {k: v for k, v in user_data.items() if k in (
        'id','first_name','last_name','email','birth_date','gender','age','like_count'
    )}

    return Response({
        "message": "Registration successful – now complete your profile!",
        "code": status.HTTP_200_OK,
        "data": {
            "user":   user_data,
            "tokens": tokens
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({
            "message": "Email and password are required.",
            "code": status.HTTP_400_BAD_REQUEST
        })

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({
            "message": "Invalid credentials.",
            "code": status.HTTP_401_UNAUTHORIZED
        })

    if not user.check_password(password):
        return Response({
            "message": "Invalid credentials.",
            "code": status.HTTP_401_UNAUTHORIZED
        })

    refresh = RefreshToken.for_user(user)
    tokens = {'refresh': str(refresh), 'access': str(refresh.access_token)}
    return Response({
        "message": "Login successful!",
        "code": status.HTTP_200_OK,
        "data": {"tokens": tokens}
    })

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({
            "message": "Refresh token is required.",
            "code": status.HTTP_400_BAD_REQUEST
        })
    try:
        RefreshToken(refresh_token).blacklist()
        return Response({
            "message": "Logout successful.",
            "code": status.HTTP_200_OK
        })
    except Exception:
        return Response({
            "message": "Invalid or expired token.",
            "code": status.HTTP_400_BAD_REQUEST
        })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile_get(request):
    user = request.user
    out = DaterSerializer(user, context={'request': request}).data
    out['age'] = _compute_age(user.birth_date)
    out['like_count'] = _compute_like_count(user)
    return Response({
        "message": "Profile fetched successfully.",
        "code": status.HTTP_200_OK,
        "data": out
    })

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile_edit(request):
    user = request.user
    data = request.data.copy()

    if 'image' in data and data['image'] is not None:
            fmt, img_str = str(data['image']).split(';base64,')
            ext = fmt.split('/')[-1]
            img_file = ContentFile(base64.b64decode(img_str), name='temp.' + ext)
            data['image'] = img_file
    else:
        data.pop('photo', None)

    serializer = DaterSerializer(user, data=data, partial=True, context={'request': request})
    if not serializer.is_valid():
        return Response({
            "message": "Validation errors.",
            "code": status.HTTP_400_BAD_REQUEST,
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    out = serializer.data
    out['age'] = _compute_age(user.birth_date)
    out['like_count'] = _compute_like_count(user)
    return Response({
        "message": "Profile updated successfully.",
        "code": status.HTTP_200_OK,
        "data": out
    })

@api_view(['GET'])
def serve_media(request, path):
    if not default_storage.exists(path):
        raise Http404(f"Media '{path}' not found")
    file_handle = default_storage.open(path, mode='rb')
    content_type, _ = mimetypes.guess_type(path)
    return FileResponse(
        file_handle,
        content_type=content_type or 'application/octet-stream',
        status=status.HTTP_200_OK
    )
