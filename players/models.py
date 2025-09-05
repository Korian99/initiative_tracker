from django.db import models


class Lobby(models.Model):
    code = models.CharField(max_length=6, unique=True)
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
        ('W', 'Weak'),
        ('N', 'Normal'),
        ('E', 'Elite'),
    )
    player = models.ForeignKey(PlayerInLobby, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    initiative = models.IntegerField()
    order = models.PositiveIntegerField(default=0)
    debuff = models.CharField(max_length=100, null= True, blank=False)
    reminder = models.CharField(max_length=100, default=None, null= True, blank=True)
    current_turn = models.BooleanField(default=False)
    stat_block = models.CharField(max_length=100, default=None, null= True, blank=True)
    template = models.CharField(max_length=1, choices=TEMPLATE_CHOICES, default='N')
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

    class Meta:
        ordering = ['-order']


class ConditionType(models.Model):
    name = models.CharField(max_length=100)


class Condition(models.Model):
    DURATION_CHOICES = (
        ('RD', 'Round Decreasing'),  # Dura X rondas
        # Cada ronda disminuye en 1 el efecto
        ('AD', 'Automatically Decreases'),
        ('MD', 'Manual Decreasing'),  # El jugador lo subira/bajara
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
            self.duration = -1
        self.save()
