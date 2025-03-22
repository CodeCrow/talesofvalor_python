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

    This will also record the starting and ending influence of the character.
    We are using both a starting and ending influence because there may be mechanics that
    change the influence between games.

    We should log when the influence changes and why.

    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, null=True, on_delete=models.SET_NULL)
    # influence tracking
    influence_start = models.IntegerField(null=True, blank=True)
    influence_end = models.IntegerField(null=True, blank=True)
    
    # number of points players get for submitting a pel on time
    ATTENDANCE_CP = 3

    # automatic influence degradation
    INFLUENCE_REGENERATION = 4

    def __str__(self):
        return "{} -- {}".format(
            self.player, self.event)
    
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
            # The user has been marked as attended:
            self.player.cp_available = models.F('cp_available') + self.ATTENDANCE_CP

        super(Attendance, self).save(*args, **kwargs)
