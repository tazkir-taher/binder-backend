
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from user_profile.serializers import ProfileSerializer
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import datetime
from datetime import date

def generate_unique_username(email):
    base_username = email.split('@')[0]
    username = base_username
    count = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{count}"
        count += 1
    return username

@api_view(['POST'])
@permission_classes([AllowAny])
def tokenObtainPair(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if "@" in email:
            user_instance = User.objects.get(email=email)
        else:
            user_instance = User.objects.filter(personal_information__phone_number__contains=email).first()
            if not user_instance:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": "No account found with these credentials. Please create your profile",
                    "status_code": 404,
                    "errors": [{"status_code": 404, "message": "No account found with these credentials"}]
                })
        
        if check_password(password, user_instance.password):
            refresh = RefreshToken.for_user(user_instance)
            return Response({
                'code': status.HTTP_200_OK,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'token_type': str(refresh.payload['token_type']),
                'expiry': refresh.payload['exp'],
                'user_id': refresh.payload['user_id'],
                'user_object':ProfileSerializer(user_instance).data,
                'profile_id': user_instance.personal_information.profile_id,
                'payment_status': user_instance.personal_information.premium_payment,
                'public': user_instance.personal_information.public,
                'payment_type': user_instance.personal_information.payment_type,
            })
        else:
            return Response({
                "code": status.HTTP_401_UNAUTHORIZED,
                "message": "Wrong password entered. If you have forgotten your password, please reset",
                "status_code": 401,
                "errors": [{"status_code": 401, "message": "Wrong password entered. If you have forgotten your password, please reset"}]
            })
    except User.DoesNotExist:
        return Response({
            "code": status.HTTP_404_NOT_FOUND,
            "message": "No account found with this credentials. Please create your profile",
            "status_code": 404,
            "errors": [{"status_code": 404, "message": "No account found with this credentials"}]
        })
    except Exception as e:
        return Response({
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": str(e),
            "status_code": 500,
            "errors": [{"status_code": 500, "message": str(e)}]
        })

@api_view(['POST'])
def tokenRefresh(request):
    try:
        refresh = RefreshToken(token=request.data.get('refresh_token'))
        return Response({
            'code': status.HTTP_200_OK,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'token_type': str(refresh.payload['token_type']),
            'expiry': refresh.payload['exp'],
            'user_id': refresh.payload['user_id'],
            'user_object': ProfileSerializer(User.objects.get(id=refresh.payload['user_id'])).data,
        })
    except Exception as e:
        return Response({
            "code": status.HTTP_401_UNAUTHORIZED,
            "message": str(e),
            "status_code": 401,
            "errors": [{"status_code": 401, "message": str(e)}]
        })

@api_view(['POST'])
def tokenVerify(request):
    try:
        verify = UntypedToken(token=request.data.get('access_token'))
        return Response({
            'code': status.HTTP_200_OK,
            'access_token': str(verify.token),
            'token_type': str(verify.payload['token_type']),
            'expiry': verify.payload['exp'],
            'user_id': verify.payload['user_id'],
        })
    except Exception as e:
        return Response({
            "code": status.HTTP_401_UNAUTHORIZED,
            "message": str(e),
            "status_code": 401,
            "errors": [{"status_code": 401, "message": str(e)}]
        })

@api_view(['POST'])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    password = request.data.get('password')
    password2 = request.data.get('password2')
    
    if password != password2:
        return Response({"password": "Passwords didn't match."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except ValidationError as e:
        return Response({"password": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
    
    User.objects.create_user(
        username=request.data['username'],
        email=request.data['email'],
        password=password
    )
    
    return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

def calculate_age(date_of_birth):
    birth_date = datetime.datetime.strptime(date_of_birth, '%Y-%m-%d')
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age