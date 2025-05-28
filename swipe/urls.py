from django.urls import path
from .views import *
urlpatterns = [
    path('like',               swipe,        name='swipe-like'),
    path('feed',               feed,         name='swipe-feed'),
    path('like/list',          likes_received, name='likes-recived'),
    path('matches',                  matches_list, name='matches-list'),
    path('matches/<int:user_id>',    match_detail, name='match-detail'),
]