from django.shortcuts import render, redirect, get_object_or_404
from players.models import Player, Lobby, Character, PlayerInLobby
from random import randint
from datetime import datetime
from django.urls import reverse
from django.views.generic import TemplateView
from django.http import HttpResponse


class LoginView(TemplateView):
    #login
    def get(self, request):
        return render(request, "players/login.html")

    #player_connect
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

        characters = Character.objects.filter(player__lobby=lobby)

        return render(request, "players/lobby.html", {'player': player_in_lobby, 'characters': characters})

    def post(self, request):
        code = str(randint(100000, 999999))  # Generate a 6-digit code
        while Lobby.objects.filter(code=code).exists():
            code = str(randint(100000, 999999))
        lobby = Lobby.objects.create(code=code, created_at=datetime.now())

        player_name = request.POST.get("player")
        player, created = Player.objects.get_or_create(name=player_name)
        PlayerInLobby.objects.create(player=player, lobby=lobby, role='DM')
        url = reverse('join_lobby')
        query_string = f"?code={lobby.code}&player={player.name}"
        return redirect(url + query_string)

def join_lobby_first_time(request):
        lobby = get_object_or_404(Lobby, code=request.GET.get("code"))
        player_name = request.GET.get("player")
        player, _ = Player.objects.get_or_create(name=player_name)
        if PlayerInLobby.objects.filter(player=player, lobby = lobby).exists():
            player_in_lobby = PlayerInLobby.objects.get(player=player, lobby = lobby)
        else:
            player_in_lobby = PlayerInLobby.objects.create(player=player, lobby = lobby, role='P')
        character_name = request.GET.get("character")
        initiative = request.GET.get("initiative")

        was_created =Character.objects.filter(
            player = player_in_lobby,
            name = character_name,
            initiative = initiative
        ).exists()

        Character.objects.update_or_create(
            player=player_in_lobby,
            name=character_name,
            defaults={'initiative': initiative}
        )
        characters = Character.objects.filter(player__lobby=lobby)

        if not was_created:
            characters = characters.order_by("-initiative")
            i=len(characters)
            for c in characters:
                c.order= i
                i-=1
                c.save()

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
        #add_character

    def get(self, request, lobby_code):
        lobby = get_object_or_404(Lobby, code=lobby_code)
        characters = Character.objects.filter(player__lobby=lobby)
        return render(request, "players/partials/character_list.html", {'characters': characters})

    #add_character
    def post(self, request):
        player_in_lobby = get_object_or_404(
            PlayerInLobby, id=request.POST.get("player"))
        lobby = player_in_lobby.lobby

        character_name = request.POST.get("character")
        initiative = request.POST.get("initiative")

        if Character.objects.filter(name=character_name, player=player_in_lobby).exists():
            existing_characters = Character.objects.filter(
                name__icontains=character_name, player=player_in_lobby)
            
            Character.objects.create(
                player=player_in_lobby,
                name=f"{character_name} ({len(existing_characters) + 1})",
                initiative=initiative
            )
        else:
            Character.objects.create(
                player=player_in_lobby, name=character_name, initiative=initiative)

        characters = Character.objects.filter(player__lobby=lobby).order_by("-initiative","-order")
        i=len(characters)
        for c in characters:
            c.order= i
            i-=1
            c.save()
        if request.headers.get("HX-Request"):
            return render(request, "players/partials/character_list.html", {'characters': characters, 'player': player_in_lobby})
        return render(request, "players/lobby.html", {'characters': characters, 'player': player_in_lobby})

class EditCharacterView(TemplateView):
    def get(self, request, player_lobby_id, character_id):

        character = get_object_or_404(Character, id=character_id)
        player_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)
        playersInLobby = PlayerInLobby.objects.filter(lobby=character.player.lobby)
        
        return render(request, "players/partials/edit_character_modal.html", {
            'character': character,
            'player_lobby': player_lobby,
            'playersInLobby': playersInLobby
        })
    
    def post(self, request):
        char_id = request.POST.get("character_id")
        new_player_id = request.POST.get("new_player")
        new_initiative = request.POST.get("initiative")
        character = get_object_or_404(Character, id=char_id)
        new_player = get_object_or_404(PlayerInLobby, id=new_player_id)
        character.player = new_player
        is_diff = int(character.initiative) != int(new_initiative)
        character.initiative = new_initiative
        character.save()
        
        lobby = character.player.lobby
        
        characters = Character.objects.filter(player__lobby=lobby)
        if is_diff:
            characters = characters.order_by("-initiative")
            i=len(characters)
            for c in characters:
                c.order= i
                i-=1
                c.save()

        player_lobby_id = request.POST.get("player_lobby_id")
        player_in_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)

        return render(request, "players/partials/character_list.html", {'characters': characters, 'player': player_in_lobby})
    
    def delete(self, request, player_lobby_id, character_id):
        character = get_object_or_404(Character, id=character_id)
        lobby = character.player.lobby 
        character.delete()
        characters = Character.objects.filter(player__lobby=lobby)
        player_in_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)
        return render(request, "players/partials/character_list.html", {'characters': characters, 'player': player_in_lobby})
    
def move_character(request):
    char_id = request.POST.get("character_id")
    player_id = request.POST.get("player_lobby_id")
    direction = request.POST.get("direction")
    
    character = get_object_or_404(Character, id=char_id)
    player = get_object_or_404(PlayerInLobby,id=player_id)

    try:
        if direction == "up":
            other_char = Character.objects.get(player__lobby=character.player.lobby, order=character.order+1)
            other_char.order -=1
            character.order +=1
        elif direction == "down":
            other_char = Character.objects.get(player__lobby=character.player.lobby, order=character.order-1)
            other_char.order +=1
            character.order -=1
        character.save()
        other_char.save()
    except:
        None
    characters = Character.objects.filter(player__lobby=character.player.lobby)

    return render(request, "players/partials/character_list.html", {'player':player, 'characters': characters})