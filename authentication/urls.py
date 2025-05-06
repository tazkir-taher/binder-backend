# urls.py (e.g. in authentication/urls.py)
from django.urls import path
from .views import register

urlpatterns = [
    path('register/', register, name='register'),
]