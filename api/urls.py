from django.urls import path, include

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('message/', include('message.urls')),
    path('swipe/', include('swipe.urls'))
]
