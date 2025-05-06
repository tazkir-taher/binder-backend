# user_profile/urls.py

from django.urls import path
from .views import profile_view

urlpatterns = [
    path('profile/', profile_view, name='user-profile'),
]
