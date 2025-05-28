from django.urls import path
from .views import *

urlpatterns = [
    path('register', register, name='register'),
    path('login',    login_view, name='login'),
    path('logout',   logout_view, name='logout'),
    path('profile', profile_get, name= 'profile'),
    path('profile/edit', profile_edit, name= 'profile-edit')
]
