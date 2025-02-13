from django.contrib import admin
from django.urls import path
from players import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('', views.LoginView.as_view(), name='player_connect'),
    path('join_lobby', views.LobbyView.as_view(), name='join_lobby'),
    path('create_lobby', views.LobbyView.as_view(), name='create_lobby'),
    path('leave_lobby', views.PlayerLobbyView.as_view(), name='leave_lobby'),
    path('lobby/<str:lobby_code>/characters/', views.CharacterView.as_view(), name='character_list_partial'),
    path('add_character', views.CharacterView.as_view(), name='add_character'),
]
