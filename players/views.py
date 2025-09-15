from django.shortcuts import render, redirect, get_object_or_404
from players.models import Player, Lobby, Character, PlayerInLobby
from random import randint
from datetime import datetime
from django.urls import reverse
from django.views.generic import TemplateView
import json
import requests
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent  # where this file lives
json_path = BASE_DIR /"database_index.json"
save_dir = BASE_DIR / "downloaded_jsons"

def reorder_characters(characters, change_turn=True):
    i = len(characters)
    for c in characters:
        c.current_turn = False
        if i == len(characters) and change_turn:
            c.current_turn = True
        c.order = i
        i -= 1
        c.save()
    return characters.order_by("-order")


def custom_404_view(request, exception):
    return redirect(reverse('login'))

def set_turn(character_id):
    if character_id:
        character = Character.objects.get(
            id=character_id)
        characters = Character.objects.filter(
            player__lobby=character.player.lobby)
        characters.filter(current_turn=True).update(current_turn=False)
        character.current_turn = True
        character.current_reactions = character.max_reactions
        character.invisible = False
        character.save()

def pass_turn(lobby):
    characters = Character.objects.filter(
        player__lobby=lobby)
    next_char = characters.first().next_turn()
    set_turn(next_char.id)



class LoginView(TemplateView):
    # login
    def get(self, request):
        return render(request, "players/login.html")

    # player_connect
    def post(self, request):
        player_name = request.POST.get("player").strip()
        if Player.objects.filter(name__iexact=player_name).exists():
            player = Player.objects.get(name__iexact=player_name)
        else:
            player = Player.objects.create(name=player_name)

        lobbies_id = PlayerInLobby.objects.filter(
            player=player).values_list("lobby_id", flat=True)
        lobbies = Lobby.objects.filter(id__in=lobbies_id)

        return render(request, "players/lobbies.html", {'player': player, 'lobbies': lobbies})


class LobbyView(TemplateView):
    # join_lobby
    def get(self, request):
        lobby = get_object_or_404(Lobby, code=request.GET.get("code"))
        player_name = request.GET.get("player")
        player = get_object_or_404(Player, name=player_name)

        # Retrieve or create the PlayerInLobby
        player_in_lobby = get_object_or_404(PlayerInLobby,
                                            player=player,
                                            lobby=lobby,
                                            )

        characters = Character.objects.filter(player__lobby=lobby)

        return render(request, "players/lobby.html", {'player': player_in_lobby, 'characters': characters})

    # create_lobby
    def post(self, request):
        code = str(randint(100000, 999999))  # Generate a 6-digit code
        while Lobby.objects.filter(code=code).exists():
            code = str(randint(100000, 999999))
        lobby = Lobby.objects.create(code=code, created_at=datetime.now())

        player_name = request.POST.get("player")
        player = get_object_or_404(Player, name=player_name)
        PlayerInLobby.objects.create(player=player, lobby=lobby, role='DM')
        url = reverse('join_lobby')
        query_string = f"?code={lobby.code}&player={player.name}"
        return redirect(url + query_string)


class EditLobbyView(TemplateView):
    # load_lobby_edit_modal
    def get(self, request, player_lobby_id):
        player_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)
        players_in_lobby = PlayerInLobby.objects.filter(
            lobby=player_lobby.lobby).exclude(role="DM")
        admin_players_ids = players_in_lobby.filter(
            role='PA').values_list("id", flat=True)
        return render(request, "players/partials/edit_lobby_modal.html", {
            'player_lobby': player_lobby, "players_in_lobby": players_in_lobby, "admin_players_ids": admin_players_ids, "lobby": player_lobby.lobby
        })

    # edit_lobby
    def post(self, request):

        player_in_lobby_id = request.POST.get("player_lobby_id")
        new_name = request.POST.get("name")
        new_pas = request.POST.getlist("players")

        player_in_lobby = PlayerInLobby.objects.get(id=player_in_lobby_id)

        lobby = player_in_lobby.lobby
        lobby.name = new_name
        lobby.save()

        notDMPlayers = PlayerInLobby.objects.filter(
            lobby=lobby).exclude(role="DM")
        notDMPlayers.update(role="P")
        notDMPlayers.filter(id__in=new_pas).update(role="PA")

        characters = Character.objects.filter(
            player__lobby=player_in_lobby.lobby)

        return render(request, "players/partials/character_list.html", {'player': player_in_lobby, 'characters': characters})


def join_lobby_first_time(request):
    lobby_code = int(request.GET.get("code"))
    player_name = request.GET.get("player")
    lobby = get_object_or_404(Lobby, code=lobby_code)
    player = get_object_or_404(Player, name=player_name)

    if PlayerInLobby.objects.filter(player=player, lobby=lobby).exists():
        player_in_lobby = PlayerInLobby.objects.get(player=player, lobby=lobby)
    else:
        player_in_lobby = PlayerInLobby.objects.create(
            player=player, lobby=lobby, role='P')
    character_name = request.GET.get("character")
    initiative = request.GET.get("initiative")

    Character.objects.update_or_create(
        player=player_in_lobby,
        name=character_name,
        defaults={'initiative': initiative}
    )

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


class PlayerView(TemplateView):
    # load_player_edit_modal
    def get(self, request, player_id, lobby_id):
        player = get_object_or_404(Player, id=player_id)

        return render(request, "players/partials/edit_player_modal.html", {
            'player': player, 'lobby_id': lobby_id
        })

    # edit_player
    def post(self, request):
        player_id = request.POST.get("player_id")
        new_name = request.POST.get("name")

        player = Player.objects.get(id=player_id)
        Player.objects.filter(id=player_id).update(name=new_name)
        lobby_id = request.POST.get("lobby_id")
        if lobby_id:
            player = PlayerInLobby.objects.get(
                player=player, lobby__id=lobby_id)
            url = reverse('join_lobby')
            query_string = f"?code={player.lobby.code}&player={player.player.name}"
            return redirect(url + query_string)
        else:
            return render(request, "players/partials/player_container.html", {'player': player})


class CharacterView(TemplateView):

    # character_list_partial
    def get(self, request, player_lobby_id):
        player = PlayerInLobby.objects.get(id=player_lobby_id)
        characters = Character.objects.filter(player__lobby=player.lobby)
        character_id =  request.GET.get("character_id", None)
        if character_id:
            character = Character.objects.get(id=character_id)
            character.current_reactions -= 1
            character.save()
        return render(request, "players/partials/character_list.html", {'player': player, 'characters': characters})

    # add_character border style for ced4da
    def post(self, request):
        player_in_lobby = get_object_or_404(
            PlayerInLobby, id=request.POST.get("player"))
        lobby = player_in_lobby.lobby

        invisible = request.POST.get("invisible", 0)
        character_name = request.POST.get("character")
        initiative = request.POST.get("initiative")
        reminder = request.POST.get("reminder")
        stat_block = request.POST.get("stat_block")
        template = request.POST.get("template", 'normal')
        max_order = Character.objects.filter(
            player__lobby=player_in_lobby.lobby).order_by("-order").first().order + 1
        if Character.objects.filter(name=character_name, player=player_in_lobby).exists():
            existing_characters = Character.objects.filter(
                name__icontains=character_name, player=player_in_lobby)
            character_name = f"{character_name} ({len(existing_characters) + 1})"
        Character.objects.create(
            player=player_in_lobby, name=character_name, initiative=initiative, reminder=reminder, order=max_order, stat_block=stat_block,
            template=template, invisible=invisible)
        characters = Character.objects.filter(
            player__lobby=lobby).order_by("-order")
        if request.headers.get("HX-Request"):
            return render(request, "players/partials/character_list.html", {'characters': characters, 'player': player_in_lobby})
        return render(request, "players/lobby.html", {'characters': characters, 'player': player_in_lobby})


class EditCharacterView(TemplateView):
    # load_char_edit_modal
    def get(self, request, player_lobby_id, character_id):

        character = get_object_or_404(Character, id=character_id)
        player_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)
        playersInLobby = PlayerInLobby.objects.filter(
            lobby=character.player.lobby)

        return render(request, "players/partials/edit_character_modal.html", {
            'character': character,
            'player_lobby': player_lobby,
            'playersInLobby': playersInLobby
        })

    # edit_character
    def post(self, request):
        char_id = request.POST.get("character_id")
        new_player_id = request.POST.get("new_player")
        character = get_object_or_404(Character, id=char_id)
        new_player = get_object_or_404(PlayerInLobby, id=new_player_id)
        character.player = new_player
        character.initiative = request.POST.get("initiative")

        character.name = request.POST.get("name")
        character.max_reactions = request.POST.get("max_reactions")
        character.current_reactions = request.POST.get("current_reactions")
        character.reminder = request.POST.get("reminder")
        character.stat_block = request.POST.get("stat_block")
        
        character.save()

        lobby = character.player.lobby

        characters = Character.objects.filter(player__lobby=lobby)

        player_lobby_id = request.POST.get("player_lobby_id")
        player_in_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)

        return render(request, "players/partials/character_list.html", {'characters': characters, 'player': player_in_lobby})

    # delete_character
    def delete(self, request, player_lobby_id, character_id):
        character = get_object_or_404(Character, id=character_id)
        lobby = character.player.lobby
        if character.current_turn:
            pass_turn(lobby)
        character.delete()
        characters = Character.objects.filter(player__lobby=lobby)
        player_in_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)
        return render(request, "players/partials/character_list.html", {'characters': characters, 'player': player_in_lobby})


class TurnView(TemplateView):
    # reload_current_turn
    def get(self, request, player_lobby_id):

        player_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)
        characters = Character.objects.filter(
            player__lobby=player_lobby.lobby).order_by("-initiative")
        characters = reorder_characters(characters)

        return render(request, "players/partials/character_list.html", {'characters': characters, 'player': player_lobby})

    # pass_turn
    def post(self, request):
        player_lobby_id = request.POST.get("player_lobby_id")
        player_in_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)
        characters = Character.objects.filter(
            player__lobby=player_in_lobby.lobby)
        pass_turn(player_in_lobby.lobby)

        return render(request, "players/partials/character_list.html", {'characters': characters, 'player': player_in_lobby})


# move_character
def move_character(request):
    player_id = request.POST.get("player_lobby_id")
    player = get_object_or_404(PlayerInLobby, id=player_id)
    characters = Character.objects.filter(
        player__lobby=player.lobby).order_by("-order")
    try:
        round_len = len(characters)
        order = request.POST.getlist('order')
        for index, character_id in enumerate(order):
            character = Character.objects.get(id=character_id)
            character.order = round_len - index  # Ensures descending order
            character.save()
    except Exception as e:
        print(e)
    characters = Character.objects.filter(
        player__lobby=player.lobby).order_by("-order")
    return render(request, "players/partials/character_list.html", {'player': player, 'characters': characters})


class DebuffView(TemplateView):
    # load_debuff_modal
    def get(self, request, player_lobby_id, character_id):

        player_lobby = get_object_or_404(PlayerInLobby, id=player_lobby_id)
        character = Character.objects.get(
            id=character_id)

        return render(request, "players/partials/debuff_modal.html", {'character': character, 'player': player_lobby})

    # debuff
    def post(self, request):
        char_id = request.POST.get("character_id")
        player_id = request.POST.get("player_lobby_id")
        debuff = request.POST.get("debuff")
        action = request.POST.get("action")

        character = get_object_or_404(Character, id=char_id)
        player = get_object_or_404(PlayerInLobby, id=player_id)

        if action == 'delete':
            character.debuff = None
        elif action == 'add_edit':
            character.debuff = debuff
        character.save()

        characters = Character.objects.filter(
            player__lobby=character.player.lobby).order_by("-order")
        return render(request, "players/partials/character_list.html", {'player': player, 'characters': characters})


class StatBlocksView(TemplateView):
    # select_creature
    def get(self, request):
        select_id = 'stat_block_add'
        default_value = ''
        character_id = request.GET.get('character_id', None)
        if character_id:
            select_id = 'stat_block_edit'
            default_value = Character.objects.get(id=character_id).stat_block
        with open(json_path, encoding="utf-8") as f:
            creatures = json.load(f)
        return render(request, "players/partials/stat_block_select.html", {"creatures": creatures, "select_id": select_id, "default_value": default_value})


class StatBlockView(TemplateView):
    # load_stat_block_modal
    def get(self, request, character_id):
        character = Character.objects.get(id=character_id)
        creature_data = character.creature
        template = request.GET.get("template", None)
        if template:
            character.template = template
            character.save()
            return render(request, "players/partials/stat_block/stat_block_data.html", {
                "creature": creature_data,
                "template": template, "character": character
            })
        return render(request, "players/partials/stat_block_modal.html", {"creature": creature_data, "template": character.template, "character": character})
