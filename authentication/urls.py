from django.urls import path
from .views import *

urlpatterns = [
    path('register', register, name='register'),
    path('login',    login_view, name='login'),
    path('logout',   logout_view, name='logout'),
    path('change-password', change_Password, name='change-password'),
    path('forgot-password', forgot_Password, name='forgot-password'),
    path('check-user', check_User_Profile_By_Email, name = 'checky-by-email'),
    path('forgot-password/verify/otp', verify_OTP, name = 'verify-OTP'),
    path('profile', profile_get, name= 'profile'),
    path('profile', images_get, name= 'profile'),
    path('profile/edit', profile_edit, name= 'profile-edit'),
    path('deactivate', profile_deactivate, name= 'profile-deactive'),
    path('delete', profile_delete, name= 'profile-deleted'),
    path('delete/<int:pk>', dater_Delete, name= 'dater-deleted')
]