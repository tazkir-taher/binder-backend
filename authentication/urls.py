from django.urls import path
from .views import *

urlpatterns = [
    path('register', register, name='register'),
    path('login',    login_view, name='login'),
    path('logout',   logout_view, name='logout'),
    path('change-password', changePassword, name='change-password'),
    path('forgot-password', forgotPassword, name='forgot-password'),
    path('check-user', checkUserProfileByEmail, name = 'checky-by-email'),
    path('forgot-password/verify/otp', verifyOTP, name = 'verify-OTP'),
    path('profile', profile_get, name= 'profile'),
    path('profile/edit', profile_edit, name= 'profile-edit'),
    path('deactivate/', profile_deactivate, name= 'profile-deactive'),
    path('delete/', profile_delete, name= 'profile-deleted')
]