from django.urls import path
from .views import *
urlpatterns = [
    path('like',               swipe,        name='swipe-like'),
    path('feed',               feed,         name='swipe-feed'),
    path('like/list',          likes_received, name='likes-recived'),
    path('search',         search,         name='search'),
    path('matches',                  matches_list, name='matches-list'),
    path('matches/<int:user_id>',    match_detail, name='match-detail'),
    path('like/<int:user_id>',    like_detail, name='match-detail'),
    path('delete/<int:pk>', connection_Delete, name='connection-delete'),
    path('delete/all', connection_Delete_all, name='connection-delete')

]