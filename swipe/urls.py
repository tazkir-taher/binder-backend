from django.urls import path
from .views import swipe_user

urlpatterns = [
    path('swipe/', swipe_user, name='swipe-user'),
]
