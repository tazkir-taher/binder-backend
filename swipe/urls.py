from django.urls import path
from .views import swipe, feed, matches_list, match_detail

urlpatterns = [
    path('swipe/like/<int:user_id>/', swipe,   name='swipe-like'),
    path('swipe/feed/',               feed,   name='swipe-feed'),
    path('matches/',                  matches_list, name='matches-list'),
    path('matches/<int:user_id>/',    match_detail, name='match-detail'),
]