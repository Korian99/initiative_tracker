from django.db import models
from django.db.models.signals import post_save, post_delete
import json
from pathlib import Path
from django.conf import settings
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class Lobby(models.Model):
    code = models.CharField(max_length=6, unique=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        if self.name is not None and len(self.name) > 0:
            return "N°"+self.code + " - "+self.name
        return "N°"+self.code


class Player(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_my_lobbies(self):
        lobbies_id = PlayerInLobby.objects.filter(
            player=self, role='DM').values_list("lobby_id", flat=True)
        lobbies = Lobby.objects.filter(id__in=lobbies_id)
        return lobbies

    def get_playing_lobbies(self):
        lobbies_id = PlayerInLobby.objects.filter(
            player=self, role__in=['PA', 'P']).values_list("lobby_id", flat=True)
        lobbies = Lobby.objects.filter(id__in=lobbies_id)
        return lobbies


class PlayerInLobby(models.Model):
    ROLE_CHOICES = (
        ('DM', 'Dungeon Master'),
        ('P', 'Player'),
        ('PA', 'Player Admin'),
    )
    role = models.CharField(max_length=2, choices=ROLE_CHOICES)
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='player')
    lobby = models.ForeignKey(
        Lobby, on_delete=models.CASCADE, related_name='lobby')

    def __str__(self):
        return "Player: "+str(self.player) + "in Lobby " + str(self.lobby)


class Character(models.Model):
    TEMPLATE_CHOICES = (
        ('weak', 'Weak'),
        ('normal', 'Normal'),
        ('elite', 'Elite'),
    )
    player = models.ForeignKey(PlayerInLobby, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    initiative = models.IntegerField()
    order = models.PositiveIntegerField(default=0)
    previous_order = models.PositiveIntegerField(default=0)
    debuff = models.CharField(max_length=100, null= True, blank=False)
    reminder = models.CharField(max_length=100, default=None, null= True, blank=True)
    invisible = models.BooleanField(default=False)
    current_turn = models.BooleanField(default=False)
    stat_block = models.CharField(max_length=100, null= True, blank=True, default= None)
    template = models.CharField(max_length=6, choices=TEMPLATE_CHOICES, default='normal')
    max_reactions = models.IntegerField(default=1)
    current_reactions = models.IntegerField(default=1)

    def __str__(self):
        return self.name + " - " + str(self.player.player)

    def next_turn(self):
        characters = Character.objects.filter(player__lobby=self.player.lobby).order_by("-order")
        current_char = characters.get(current_turn=True)
        next_chars = characters.filter(order__lt=current_char.order)
        if next_chars.exists():
            return next_chars.first()
        else:
            return characters.first()
        
    @property
    def creature(self):
        """Load JSON content from jsons/ folder based on `path`"""
        jsons_dir = Path(settings.BASE_DIR) / "jsons"
        file_path = jsons_dir / f"{self.stat_block.replace(' ', '_')}.json"
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                return {"error": str(e)}
        return None
    
    class Meta:
        ordering = ['-order']


@receiver([post_save, post_delete], sender=Character)
def character_changed(sender, instance, **kwargs):
    lobby_id = str(instance.player.lobby.id)
    channel_layer = get_channel_layer()
    # Trigger the consumer to broadcast
    async_to_sync(channel_layer.group_send)(
        lobby_id,
        {
            "type": "send_update",
            "message": "list"
        }
    )

@receiver([post_save, post_delete], sender=Lobby)
def lobby_changed(sender, instance, **kwargs):
    lobby_id = str(instance.id)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        lobby_id,
        {
            "type": "send_update",
            "message": "lobby"
        }
    )