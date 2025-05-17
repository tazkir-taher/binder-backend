from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view),
    path('media/<path:path>/', views.serve_media),
]