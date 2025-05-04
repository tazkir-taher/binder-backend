from django.urls import path
from .views import ProfileDetailView

urlpatterns = [
    path('user_profile/', ProfileDetailView.as_view(), name='profile-detail'),
]