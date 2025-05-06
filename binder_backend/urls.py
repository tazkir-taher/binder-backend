from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('home/', include('swipe.urls')),
    path('user/', include('user_profile.urls')),
]