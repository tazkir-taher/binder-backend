from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .models import Dater
from .serializers import *
from datetime import timedelta
from django.utils import timezone
from rest_framework import status

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        serializer = PhoneRegisterSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            
            user = Dater.objects.create(
                phone_number=phone_number,
                username=phone_number,
                is_active=True,
                is_verified=False,
                profile_completed=False
            )
            
            otp = user.generate_otp()
            print(f"Registration OTP for {phone_number}: {otp}")
            
            return Response({
                'code': status.HTTP_201_CREATED,
                'message': 'Registration initiated. Verify phone number.',
                'dater_id': user.id
            })
        
        return Response({
            'code': status.HTTP_400_BAD_REQUEST,
            'message': 'Invalid data',
            'errors': serializer.errors
        })

    except Exception as e:
        return Response({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': str(e)
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    try:
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Phone number is required'
            })
        user = Dater.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'No account found with this phone number'
            })
        otp = user.generate_otp()
        print(f"OTP for {phone_number}: {otp}")
        return Response({
            'code': status.HTTP_200_OK,
            'message': 'OTP sent successfully',
            'dater_id': user.id
        })
    except Exception as e:
        return Response({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': str(e)
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    try:
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid data',
                'errors': serializer.errors
            })

        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        
        user = Dater.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'No account found'
            })
        
        if user.verify_otp(otp):
            refresh = RefreshToken.for_user(user)
            return Response({
                'code': status.HTTP_200_OK,
                'message': 'Phone verified! Complete profile in dashboard',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'profile_completed': user.profile_completed
            })
        
        return Response({
            'code': status.HTTP_400_BAD_REQUEST,
            'message': 'Invalid/expired OTP'
        })

    except Exception as e:
        return Response({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': str(e)
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid data',
                'errors': serializer.errors
            })

        phone_or_email = serializer.validated_data['phone_or_email']
        password = serializer.validated_data['password']
        
        if '@' in phone_or_email:
            user = Dater.objects.filter(email=phone_or_email).first()
        else:
            user = Dater.objects.filter(phone_number=phone_or_email).first()
        
        if not user:
            return Response({
                'code': status.HTTP_401_UNAUTHORIZED,
                'message': 'Invalid credentials'
            })
        
        if not user.is_verified:
            return Response({
                'code': status.HTTP_403_FORBIDDEN,
                'message': 'Verify phone number first'
            })
        
        if not user.profile_completed:
            return Response({
                'code': status.HTTP_403_FORBIDDEN,
                'message': 'Complete profile in dashboard'
            })
        
        if not check_password(password, user.password):
            return Response({
                'code': status.HTTP_401_UNAUTHORIZED,
                'message': 'Invalid credentials'
            })
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'code': status.HTTP_200_OK,
            'message': 'Login successful',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'profile_completed': user.profile_completed
        })

    except Exception as e:
        return Response({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': str(e)
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def tokenObtainPair(request):
    try:
        login_serializer = LoginSerializer(data=request.data)
        if login_serializer.is_valid():
            phone_or_email = login_serializer.validated_data.get('phone_or_email')
            password = login_serializer.validated_data.get('password')
            if '@' in phone_or_email:
                user = Dater.objects.filter(email=phone_or_email).first()
            else:
                if len(phone_or_email) < 9:
                    return Response({
                        "code": status.HTTP_403_FORBIDDEN,
                        "message": "Not a valid phone number",
                        "errors": [{"message": "Not a valid phone number"}]
                    })
                user = Dater.objects.filter(phone_number=phone_or_email).first()
            if not user:
                return Response({
                    "code": status.HTTP_401_UNAUTHORIZED,
                    "message": "No account found with these credentials. Please register",
                    "errors": [{"message": "Account not found"}]
                })
            if not user.is_verified:
                return Response({
                    "code": status.HTTP_403_FORBIDDEN,
                    "message": "Account not verified. Please verify your phone number",
                    "errors": [{"message": "Account not verified"}]
                })
            if not user.profile_completed:
                return Response({
                    "code": status.HTTP_403_FORBIDDEN,
                    "message": "Profile not completed. Please complete your profile",
                    "errors": [{"message": "Profile not completed"}]
                })
            if not check_password(password, user.password):
                return Response({
                    "code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Wrong password entered",
                    "errors": [{"message": "Invalid credentials"}]
                })
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({
                'code': status.HTTP_200_OK,
                'access_token': access_token,
                'refresh_token': str(refresh),
                'token_type': 'bearer',
                'expiry': refresh.payload['exp'],
                'dater_id': user.id,
                'is_verified': user.is_verified,
                'profile_completed': user.profile_completed,
                'phone_number': user.phone_number
            })
        return Response({
            'code': status.HTTP_400_BAD_REQUEST,
            'message': 'Invalid login data',
            'errors': login_serializer.errors
        })
    except Exception as e:
        return Response({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': str(e)
        })
