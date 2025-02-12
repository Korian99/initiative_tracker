from django.shortcuts import render, redirect

# Create your views here.
def login(request):
    return render(request, "players/login.html")

def join_lobby(request):
    return render(request, "players/lobby.html")

def create_lobby(request):
    return redirect('create_lobby')
