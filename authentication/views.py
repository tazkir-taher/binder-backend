import base64
import mimetypes
from datetime import date

from django.http import FileResponse, Http404
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from system_manager.helper import generate_unique_numeric_otp
from .models import *
from .serializers import *

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    pw, pw2 = data.get('password'), data.get('password2')

    if not pw or not pw2:
        return Response(
            {
                "message": "Both password fields are required.",
                "code": status.HTTP_400_BAD_REQUEST
            }
        )
    if pw != pw2:
        return Response(
            {"message": "Passwords do not match.",
             "code": status.HTTP_400_BAD_REQUEST}
        )

    serializer = DaterRegistrationSerializer(data=data)
    if not serializer.is_valid():
        return Response(
            {
                "message": "Validation errors.",
                "code": status.HTTP_400_BAD_REQUEST,
                "data": serializer.errors,
            }
        )

    birth = serializer.validated_data.get('birth_date')
    if birth:
        today = date.today()
        years = today.year - birth.year
        had_bday = (today.month, today.day) >= (birth.month, birth.day)
        age = years if had_bday else years - 1
        if age < 18:
            return Response(
                {
                    "message": "You must be at least 18 to register.",
                    "code": status.HTTP_400_BAD_REQUEST,
                }
            )

    user_data = serializer.validated_data.copy()
    user_data.pop('password2')
    raw_password = user_data.pop('password')

    try:
        user = User(**user_data)
        user.set_password(raw_password)
        user.save()
    except IntegrityError as e:
        return Response(
            {
                "message": f"Error creating user: {e}",
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        )

    refresh = RefreshToken.for_user(user)
    tokens = {"refresh": str(refresh),
              "access": str(refresh.access_token)}

    user_data = DaterSerializer(user, context={'request': request}).data
    user_data = {
        k : v
        for k, v in user_data.items()
        if k
        in ('id', 'first_name', 'last_name', 'email', 'birth_date', 'gender', 'age', 'like_count')
    }

    return Response(
        {
            "message": "Registration successful GO COMPLETE YO PROFILE!",
            "code": status.HTTP_200_OK,
            "data": {"user": user_data,
                     "tokens": tokens}
        }
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {
                "message": "Email and password are required.",
                "code": status.HTTP_400_BAD_REQUEST
            }
        )

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response(
            {"message": "Invalid credentials.", 
             "code": status.HTTP_401_UNAUTHORIZED}
        )

    if user.is_deleted:
        return Response(
            {
                "message": "Your account has been deleted permanently. Please register again.",
                "code": status.HTTP_403_FORBIDDEN
            }
        )

    if not user.check_password(password):
        return Response(
            {"message": "Invalid credentials. The password is not correct.", 
             "code": status.HTTP_401_UNAUTHORIZED}
        )
    
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=['is_active'])
        refresh = RefreshToken.for_user(user)
        tokens = {"refresh": str(refresh),
                  "access": str(refresh.access_token)}
        return Response(
            {
                "message": "Account reactivated! Welcome back!",
                "code": status.HTTP_200_OK,
                "data": {"tokens": tokens}
            }
        )

    refresh = RefreshToken.for_user(user)
    tokens = {"refresh": str(refresh),
              "access": str(refresh.access_token)}
    return Response(
        {
            "message": "Login successful!",
            "code": status.HTTP_200_OK,
            "data": {"tokens": tokens}
        }
    )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {
                "message": "Refresh token is required.",
                "code": status.HTTP_400_BAD_REQUEST,
            }
        )
    try:
        RefreshToken(refresh_token).blacklist()
        return Response({"message": "Logout successful.",
                         "code": status.HTTP_200_OK})
    except Exception:
        return Response(
            {"message": "Invalid or expired token.",
             "code": status.HTTP_400_BAD_REQUEST}
        )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_Password(request):
    try:
        data = request.data
        user = request.user
        serializer = ChangePasswordSerializer(data=data)

        if serializer.is_valid():
            password = serializer.data.get('new_password1')
            password2 = serializer.data.get('new_password2')
            if password != password2:
                raise serializers.ValidationError({"password": "Passwords Must Match"})

            user.set_password(password2)
            user.save(update_fields=['password'])

            return Response(
                {
                    "response": "Password updated successfully.",
                    "code": status.HTTP_200_OK,
                    "data": serializer.data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {"code": status.HTTP_400_BAD_REQUEST,
             "response": "Data not Found",
             "error": str(e)}
        )

@api_view(['POST'])
def check_User_Profile_By_Email(request):
    try:
        data = request.data
        email = data.get('email')

        try:
            user = User.objects.get(email=email)
            otp = generate_unique_numeric_otp(ProfilesHasOTP)
            ProfilesHasOTP.objects.create(user=user, otp=otp)
            return Response(
                {
                    "response": "User Profile Found",
                    "status": status.HTTP_200_OK,
                    "email": user.email,
                    "user": user.id,
                    "otp": otp,
                }
            )
        except User.DoesNotExist:
            return Response({"response": "No Profile Found", "status": 400})
    except Exception as e:
        return Response(
            {"code": status.HTTP_400_BAD_REQUEST,
             "response": "Data not Found",
             "error": str(e)}
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_OTP(request):
    try:
        user_id = request.data.get('user')
        user_instance = User.objects.get(id=user_id)
        latest_otp_record = ProfilesHasOTP.objects.filter(user=user_instance).latest('id')

        if latest_otp_record:
            user_entered_otp = request.data.get('otp')
            if user_entered_otp == latest_otp_record.otp:
                latest_otp_record.verified = True
                latest_otp_record.save()

                return Response(
                    {'code': status.HTTP_200_OK,
                     'response': "OTP verified successfully"
                    }
                )
            else:
                return Response({'code': status.HTTP_400_BAD_REQUEST,
                                 'response': "Invalid OTP"})
        else:
            return Response({'code': status.HTTP_400_BAD_REQUEST,
                             'response': "No OTP record found for verification"})

    except Exception as e:
        return Response({'code': status.HTTP_400_BAD_REQUEST,
                         'response': "Error in OTP verification",
                         "error": str(e)})

@api_view(['POST'])
def forgot_Password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    try:
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            new_password = serializer.validated_data.get('new_password1')
            new_password2 = serializer.validated_data.get('new_password2')

            if new_password != new_password2:
                return Response(
                    {"response": "Passwords do not match.",
                    "code": status.HTTP_400_BAD_REQUEST}
                )

            try:
                account = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"response": "No Profile Found",
                                "code": status.HTTP_400_BAD_REQUEST})

            if not ProfilesHasOTP.objects.filter(user=account, verified=True).exists():
                return Response(
                    {
                        "response": "OTP not verified. Please verify OTP before resetting password.",
                        "code": status.HTTP_400_BAD_REQUEST,
                    }
                )

            account.set_password(new_password2)
            account.save()

            return Response({
                "response": "Password reset successfully.",
                'code': status.HTTP_200_OK,
                'data': serializer.data
            })

        return Response({

            "response": serializer.errors,
            "code": status.HTTP_400_BAD_REQUEST

        })

    except Exception as e:
        return Response({
            'code': status.HTTP_400_BAD_REQUEST,
            'response': "Data not Found",
            'error': str(e)
        })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile_get(request):
    user = request.user
    out = DaterSerializer(user, context={'request': request}).data
    return Response({"message": "Profile fetched successfully.",
                     "code": status.HTTP_200_OK,
                     "data": out})

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
        return Response(
            {
                "message": "Validation errors.",
                "code": status.HTTP_400_BAD_REQUEST,
                "data": serializer.errors,
            }
        )

    serializer.save()
    edited_data = serializer.data

    return Response({"message": "Profile updated successfully.",
                     "code": status.HTTP_200_OK,
                     "data": edited_data})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile_deactivate(request):
    user = request.user
    if user.is_deleted:
        return Response(
            {"message": "Cannot deactivate. Your account is already deleted.",
             "code": status.HTTP_400_BAD_REQUEST}
        )

    if not user.is_active:
        return Response({"message": "Your account is already deactivated.",
                         "code": status.HTTP_200_OK})

    user.is_active = False
    user.save(update_fields=['is_active'])
    return Response({"message": "Account deactivated. GOOD BYE", 
                    "code": status.HTTP_200_OK})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile_delete(request):
    user = request.user
    if user.is_deleted:
        return Response(
            {"message": "Your account is already deleted. Please register again if you want to return.", 
             "code": status.HTTP_400_BAD_REQUEST}
        )

    user.is_deleted = True
    user.is_active = False
    user.save(update_fields=['is_deleted', 'is_active'])
    return Response(
        {"message": "Account marked as deleted. GOOD BYE", 
         "code": status.HTTP_200_OK}
    )

@api_view(['GET'])
def serve_media(request, path):
    if not default_storage.exists(path):
        raise Http404(f"Media '{path}' not found")
    file_handle = default_storage.open(path, mode='rb')
    content_type, _ = mimetypes.guess_type(path)
    return FileResponse(
        file_handle, content_type=content_type or 'application/octet-stream', status=status.HTTP_200_OK
    )