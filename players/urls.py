from django.contrib import admin
from django.urls import path
from players import views

urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('player_connect', views.LoginView.as_view(), name='player_connect'),
    path('join_lobby', views.LobbyView.as_view(), name='join_lobby'),
    path('join_lobby_first_time', views.join_lobby_first_time, name='join_lobby_first_time'),
    path('create_lobby', views.LobbyView.as_view(), name='create_lobby'),
    path('leave_lobby', views.PlayerLobbyView.as_view(), name='leave_lobby'),
    path('lobby/<str:player_lobby_id>/characters/', views.CharacterView.as_view(), name='character_list_partial'),
    path('add_character', views.CharacterView.as_view(), name='add_character'),
    path('move_character', views.move_character, name='move_character'),
    path('edit_character/', views.EditCharacterView.as_view(), name='edit_character'),
    path('load_char_edit_modal/<int:player_lobby_id>/<int:character_id>/', views.EditCharacterView.as_view(), name='load_char_edit_modal'),
    path('delete_character/<int:player_lobby_id>/<int:character_id>/', views.EditCharacterView.as_view(), name='delete_character'),
    path('load_lobby_edit_modal/<int:player_lobby_id>/', views.EditLobbyView.as_view(), name='load_lobby_edit_modal'),
    path('edit_lobby', views.EditLobbyView.as_view(), name='edit_lobby'),
]
