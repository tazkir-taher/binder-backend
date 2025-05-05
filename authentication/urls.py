from django.urls import path
from .views import (
    register,
    send_otp,
    verify_otp,
    complete_profile,
    login,
    tokenObtainPair,
    tokenRefresh,
    tokenVerify,
    tokenBlacklist,
    passwordResetRequest,
    passwordResetConfirm,
)

urlpatterns = [
    # Registration flow
    path('register/', register, name='register'),  # Initial registration with phone
    path('send-otp/', send_otp, name='send_otp'),  # Send/resend OTP
    path('verify-otp/', verify_otp, name='verify_otp'),  # Verify OTP
    path('complete-profile/', complete_profile, name='complete_profile'),  # Complete profile after verification
    path('login/', login, name='login'),  # Login with phone/email and password
    
    # Token management
    path('token/', tokenObtainPair, name='token_obtain_pair'),  # Get JWT tokens
    path('token/refresh/', tokenRefresh, name='token_refresh'),  # Refresh JWT token
    path('token/verify/', tokenVerify, name='token_verify'),  # Verify JWT token
    path('token/blacklist/', tokenBlacklist, name='token_blacklist'),  # Logout (blacklist token)
    
    # Password management
    path('password/reset/', passwordResetRequest, name='password_reset'),  # Request password reset
    path('password/reset/confirm/', passwordResetConfirm, name='password_reset_confirm'),  # Confirm password reset
]