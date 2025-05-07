from django.urls import path
from . import views

urlpatterns = [
    path('swipe/feed/', views.swipe_feed, name='swipe-feed'),
    path('swipe/', views.swipe_post, name='swipe-post'),
    path('matches/', views.matches_list, name='matches-list'),
    path('matches/<int:user_id>/', views.match_detail, name='match-detail')
]
