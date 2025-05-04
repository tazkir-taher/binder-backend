from django.urls import path
from . import views
from .views import register_view

urlpatterns = [
    path('auth/token/', views.tokenObtainPair, name='token_obtain_pair'),
    path('auth/token/refresh/', views.tokenRefresh, name='token_refresh'),
    path('auth/token/verify/', views.tokenVerify, name='token_verify'),
    path('register/', register_view, name='register'),
]
