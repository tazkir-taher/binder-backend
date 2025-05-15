from django.urls import path
from .views import swipe_feed, swipe_post, matches_list, match_detail

urlpatterns = [
    path('swipe/feed/',      swipe_feed,    name='swipe-feed'),
    path('swipe/',           swipe_post,    name='swipe-post'),
    path('matches/',         matches_list,  name='matches-list'),
    path('matches/<int:user_id>/', match_detail, name='match-detail'),
]
