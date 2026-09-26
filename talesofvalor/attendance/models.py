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

    Marking a player as attended grants them the attendance points.

    If this is a player's first event, their record is updated for the
    field "game_started".  Once it is set it is left alone, so a staff
    correction on the player form sticks.

    Deleting the attendance undoes both: the points are taken back and
    "game_started" moves to whatever event the player now attended first.

    Influence is tracked per event in ``characters.CharacterEventInfluence``
    rather than here, so that it can be entered, processed and reversed
    independently of attendance.
    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, null=True, on_delete=models.SET_NULL)

    # number of points players get for submitting a pel on time
    ATTENDANCE_CP = 3

    def __str__(self):
        return "{} -- {}".format(
            self.player, self.event)
    
    def save(self, *args, **kwargs):
        """
        Save the attendance.

        When we do this, we should copy the character from the previous
        attendance if it is not already set, grant the player the points for
        having attended, and record the event their game started at.
        """
        if self.pk is None:
            # if this is new attendance and not an update, fall back to the
            # character the player is currently playing.  Check the id, so
            # an unset character doesn't go looking for a related object.
            if self.character_id is None:
                self.character = self.player.active_character

            player_fields = []
            # The player has been marked as attended, so grant the points.
            # There is no unique constraint on (player, event), so look
            # first: a second row for the same event is a duplicate, not a
            # second attendance to be paid for.
            already_attended = Attendance.objects\
                .filter(player=self.player, event=self.event)\
                .exists()
            if not already_attended:
                self.player.cp_available = models.F('cp_available') +\
                    self.ATTENDANCE_CP
                player_fields.append('cp_available')
            # the first event a player attends is where their game started.
            # never overwrite it: staff correct it on the player form.
            if self.player.game_started_id is None:
                self.player.game_started = self.event
                player_fields.append('game_started')
            if player_fields:
                self.player.save(update_fields=player_fields)
                if 'cp_available' in player_fields:
                    # the F() expression is still sitting on the instance, so
                    # read the stored value back rather than leaving callers
                    # holding an expression object.
                    self.player.refresh_from_db(fields=['cp_available'])

        super(Attendance, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Remove the attendance, undoing what saving it did.

        The points are taken back, and if this was the event the player's
        game started at, that moves to whatever they now attended first.
        """
        player = self.player
        event = self.event
        # only take the points back if this is the last row for the event.
        # a duplicate never got paid for, so removing one shouldn't charge
        # the player for it.
        was_only_row = not Attendance.objects\
            .filter(player=player, event=event)\
            .exclude(pk=self.pk)\
            .exists()

        result = super(Attendance, self).delete(*args, **kwargs)

        player_fields = []
        if was_only_row:
            # worked out in python rather than with an F() expression:
            # cp_available can't go negative, and on MySQL an unsigned
            # column would fail rather than stop at zero.
            player.refresh_from_db(fields=['cp_available'])
            player.cp_available = max(
                0, player.cp_available - self.ATTENDANCE_CP)
            player_fields.append('cp_available')
        # only move game_started if it pointed at the event being removed,
        # so a staff correction on the player form is left alone.
        if player.game_started_id == event.id:
            first_attendance = Attendance.objects\
                .filter(player=player)\
                .order_by('event__event_date')\
                .first()
            player.game_started = first_attendance.event \
                if first_attendance else None
            player_fields.append('game_started')
        if player_fields:
            player.save(update_fields=player_fields)

        return result
