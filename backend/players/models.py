from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    ROLE_CHOICES = (
        ('DM', 'Dungeon Master'),
        ('P', 'Player'),
        ('PA', 'Player Admin'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=2, choices=ROLE_CHOICES)

class Lobby(models.Model):
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    dm = models.ForeignKey(Player, on_delete=models.CASCADE)

class Character(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=100)
    initiative = models.IntegerField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-initiative']  # auto-order by initiative but allow manual reordering
