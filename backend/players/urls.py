from django.contrib import admin
from django.urls import path
from players import views

urlpatterns = [
    path('', views.login, name='login'),
    path('player_connect', views.player_connect, name='player_connect'),
    path('join_lobby', views.join_lobby, name='join_lobby'),
    path('create_lobby', views.create_lobby, name='create_lobby'),
    path('lobby/<str:lobby_code>/characters/', views.character_list_partial, name='character_list_partial'),
    path('add_character', views.add_character, name='add_character'),
]
