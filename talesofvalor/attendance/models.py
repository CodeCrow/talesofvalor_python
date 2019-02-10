"""
Describes the attendance at a game event.

These models indicate who has attended what event as
which character.

It is a separate app because if it was included in Event, Character
or Player, it creates a circular dependency.
"""
from django.db import models

from talesofvalor.players.models import Player
from talesofvalor.characters.models import Character
from talesofvalor.events.models import Event


class Attendance(models.Model):
    """
    Attendance at an event.

    Indicates if a PLAYER has attended an EVENT as a specific
    CHARACTER.

    If this is a player's first event, their record is updated for the
    field "game_started"
    """

    player = models.ForeignKey(Player)
    event = models.ForeignKey(Event)
    character = models.ForeignKey(Character)
