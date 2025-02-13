from django.shortcuts import render, redirect, get_object_or_404
from players.models import Player, Lobby, Character, PlayerInLobby
from random import randint
from datetime import datetime
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import HttpResponse


class LoginView(TemplateView):
    def get(self, request):
        return render(request, "players/login.html")

    def post(self, request):
        player_name = request.POST.get("player")
        player, _ = Player.objects.get_or_create(name=player_name)

        lobbies_id = PlayerInLobby.objects.filter(
            player=player).values_list("lobby_id", flat=True)
        lobbies = Lobby.objects.filter(id__in=lobbies_id)

        return render(request, "players/lobbies.html", {'player': player, 'lobbies': lobbies})


class LobbyView(TemplateView):
    def get(self, request):
        lobby = get_object_or_404(Lobby, code=request.GET.get("code"))
        player_name = request.GET.get("player")

        # Retrieve or create the Player
        player, created = Player.objects.get_or_create(name=player_name)

        # Retrieve or create the PlayerInLobby
        player_in_lobby, created = PlayerInLobby.objects.get_or_create(
            player=player,
            lobby=lobby,
            defaults={'role': 'P'}  # Default role is 'Player'
        )

        # Handle character creation or update if 'character' is in GET parameters
        character_name = request.GET.get("character")
        initiative = request.GET.get("initiative")
        if character_name and initiative:
            Character.objects.update_or_create(
                player=player_in_lobby,
                name=character_name,
                defaults={'initiative': initiative}
            )

        # Retrieve all characters in the lobby
        characters = Character.objects.filter(player__lobby=lobby)

        return render(request, "players/lobby.html", {'player': player_in_lobby, 'characters': characters})

    def post(self, request):
        code = str(randint(100000, 999999))  # Generate a 6-digit code
        while Lobby.objects.filter(code=code).exists():
            code = str(randint(100000, 999999))
        lobby = Lobby.objects.create(code=code, created_at=datetime.now())

        player_name = request.POST.get("player")
        player, created = Player.objects.get_or_create(name=player_name)

        # Associate the player with the lobby as the Dungeon Master
        PlayerInLobby.objects.create(player=player, lobby=lobby, role='DM')

        # Redirect to the join_lobby view
        url = reverse('join_lobby')
        query_string = f"?code={lobby.code}&player={player.name}"
        return redirect(url + query_string)


class PlayerLobbyView(TemplateView):
    def post(self, request):
        player_name = request.POST.get("player")
        code = request.POST.get("code")
        player = Player.objects.get(name=player_name)
        pil = PlayerInLobby.objects.get(
            player=player, lobby__code=code)
        if pil.role == 'DM':
            pil.lobby.delete()
        pil.delete()
        if request.headers.get("HX-Request"):
            return render(request, "players/partials/lobby_list.html", {'player': player})
        lobbies_id = PlayerInLobby.objects.filter(
            player=player).values_list("lobby_id", flat=True)
        lobbies = Lobby.objects.filter(id__in=lobbies_id)
        return render(request, "players/lobbies.html", {'player': player, 'lobbies': lobbies})


class CharacterView(TemplateView):
    def get(self, request, lobby_code):
        lobby = get_object_or_404(Lobby, code=lobby_code)
        characters = Character.objects.filter(player__lobby=lobby)
        return render(request, "players/partials/character_list.html", {'characters': characters})

    def post(self, request):
        player_in_lobby = get_object_or_404(
            PlayerInLobby, id=request.POST.get("player"))
        lobby = player_in_lobby.lobby

        character_name = request.POST.get("character")
        initiative = request.POST.get("initiative")

        # Check if a character with the same name exists for the player in the lobby
        if Character.objects.filter(name=character_name, player=player_in_lobby).exists():
            existing_characters = Character.objects.filter(
                name=character_name, player=player_in_lobby)
            Character.objects.create(
                player=player_in_lobby,
                name=f"{character_name} ({len(existing_characters) + 1})",
                initiative=initiative
            )
        else:
            Character.objects.create(
                player=player_in_lobby, name=character_name, initiative=initiative)

        characters = Character.objects.filter(player__lobby=lobby)

        if request.headers.get("HX-Request"):
            return render(request, "players/partials/character_list.html", {'characters': characters})
        return render(request, "players/lobby.html", {'characters': characters, 'player': player_in_lobby})
