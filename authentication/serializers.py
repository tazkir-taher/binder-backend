from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import OTP

Dater = get_user_model()  # Get our custom Dater model

class PhoneRegisterSerializer(serializers.Serializer):
    """Serializer to handle initial phone number registration"""
    phone_number = serializers.CharField(max_length=15, required=True)
    
    def validate_phone_number(self, value):
        """Validate that phone number doesn't already exist"""
        if Dater.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    """Serializer to verify OTP code during registration"""
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

class CompleteProfileSerializer(serializers.ModelSerializer):
    """Serializer to complete user profile after phone verification"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Dater
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']
        
    def validate(self, attrs):
        """Validate that password and password confirmation match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

class LoginSerializer(serializers.Serializer):
    """Serializer for user login with phone or email"""
    phone_or_email = serializers.CharField()
    password = serializers.CharField()

class TokenObtainPairSerializer(serializers.Serializer):
    """Serializer for obtaining JWT tokens"""
    phone_or_email = serializers.CharField()
    password = serializers.CharField()

class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for refreshing JWT tokens"""
    refresh_token = serializers.CharField()

class TokenVerifySerializer(serializers.Serializer):
    """Serializer for verifying JWT tokens"""
    access_token = serializers.CharField()

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset"""
    phone_or_email = serializers.CharField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset with OTP"""
    phone_or_email = serializers.CharField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        """Validate that new password and confirmation match"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs