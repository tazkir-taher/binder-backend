from django.urls import path
from . import views

urlpatterns = [
    path('send/',      views.send_message,    name='send-message'),
    path('thread/<int:user_id>/', views.get_conversation, name='get-conversation'),
    path('recent/',    views.recent_chats,     name='recent-chats'),
]