"""
Describes the player models.

These models describe the player and its relationship to the
django authentication user models.
"""
from django.contrib.auth.models import User
from django.db import models

from talesofvalor.events.models import Event

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game_started = models.ForeignKey(Event, null=True)
    cp_available = models.PositiveIntegerField(default=0)