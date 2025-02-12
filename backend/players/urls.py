from django.contrib import admin
from django.urls import path
from players import views

urlpatterns = [
    path('', views.login),
    path('join_lobby', views.join_lobby),
    path('create_lobby', views.create_lobby),
]
