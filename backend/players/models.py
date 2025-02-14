from django.db import models
from django.contrib.auth.models import User


class Lobby(models.Model):
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        if self.name is not None and len(self.name)>0:
            return self.name
        return "N°"+self.code            
class Player(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name  
    def get_my_lobbies(self):
        lobbies_id = PlayerInLobby.objects.filter(player=self, role='DM').values_list("lobby_id",flat=True)
        lobbies = Lobby.objects.filter(id__in=lobbies_id)
        return lobbies
    
    def get_playing_lobbies(self):
        lobbies_id = PlayerInLobby.objects.filter(player=self, role__in=['PA','P']).values_list("lobby_id",flat=True)
        lobbies = Lobby.objects.filter(id__in=lobbies_id)
        return lobbies
    
class PlayerInLobby(models.Model):
    ROLE_CHOICES = (
        ('DM', 'Dungeon Master'),
        ('P', 'Player'),
        ('PA', 'Player Admin'),
    )
    role = models.CharField(max_length=2, choices=ROLE_CHOICES)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player')
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='lobby')
    def __str__(self):
        return "Player: "+str(self.player) + "in Lobby " + str(self.lobby)   

class Character(models.Model):
    player = models.ForeignKey(PlayerInLobby, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    initiative = models.IntegerField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name + " - " + str(self.player.player)  
    class Meta:
        ordering = ['-order']  # auto-order by initiative but allow manual reordering

class ConditionType(models.Model):
    name = models.CharField(max_length=100)

class Condition(models.Model):
    DURATION_CHOICES = (
        ('RD', 'Round Decreasing'), #Dura X rondas 
        ('AD', 'Automatically Decreases'), #Cada ronda disminuye en 1 el efecto
        ('MD', 'Manual Decreasing'), #El jugador lo subira/bajara
    )
    durationType = models.CharField(max_length=2, choices=DURATION_CHOICES)
    conditionType = models.ForeignKey(ConditionType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class CharacterCondition(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    duration = models.IntegerField()

    def decrease_duration(self, value=None):
        if value is not None:
            self.duration = value
        elif self.condition.durationType in {'RD', 'AD'}:
            self.duration =-1
        self.save()
