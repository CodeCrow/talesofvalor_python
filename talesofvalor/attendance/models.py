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

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        """
        Save the attendance.

        When we do this, we should copy the character from the previous
        attendance if it is not already set.
        """
        if self.pk is None:
            # if this is new attendance and not an update, take information
            # from the previous one if it isn't updated.
            if not hasattr(self, 'character'):
                # Now, check the current active character
                self.character = self.player.active_character

        super(Attendance, self).save(*args, **kwargs)
