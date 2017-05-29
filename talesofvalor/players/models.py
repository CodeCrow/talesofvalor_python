"""
Describes the player models.

These models describe the player and its relationship to the
django authentication user models.
"""
from django.contrib.auth.models import User
from django.db import models


class Player(models.Model):
    """
    Player of a game.

    An individual who is playing a game.  All users are players
    of some sort.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game_started = models.ForeignKey(Event, null=True)
    cp_available = models.PositiveIntegerField(default=0)
