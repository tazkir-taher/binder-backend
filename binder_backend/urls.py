from django.contrib import admin
from django.urls import path, include, re_path
from user_profile.views import serve_media

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('home/', include('swipe.urls')),
    path('user/', include('user_profile.urls')),
    path('messages/', include('message.urls')),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve_media, name='serve-media'),
]