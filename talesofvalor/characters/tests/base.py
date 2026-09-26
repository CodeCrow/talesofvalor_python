"""
Shared set up for influence tests.

Influence spans characters and events, so both apps' tests build the same
small world: a staff user, a player with a character, and events they
attended.
"""
from datetime import date, timedelta

from cms.utils.permissions import set_current_user

from django.contrib.auth.models import User
from django.test import TestCase

from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character, CharacterEventInfluence
from talesofvalor.events.models import Event


class InfluenceTestCase(TestCase):
    """A staff user, a player with a character, and helpers for events."""

    def setUp(self):
        # django-cms remembers the logged in user in a threadlocal that
        # outlives a test.  Left set, creating a user here would stamp it as
        # created by somebody the previous test has already rolled back.
        set_current_user(None)
        self.staff = User.objects.create_user(
            username='staff',
            password='secret'
        )
        # a Player is created automatically by a post_save signal on User.
        self.player_user = User.objects.create_user(
            username='player',
            password='secret'
        )
        self.player = self.player_user.player
        self.character = Character.objects.create(
            player=self.player,
            name="Aldric",
            active_flag=True
        )

    def make_event(self, name, days_out=0):
        event_date = date.today() + timedelta(days=days_out)
        return Event.objects.create(
            name=name,
            event_date=event_date,
            pel_due_date=event_date + timedelta(days=7),
            bgs_due_date=event_date + timedelta(days=7)
        )

    def attend(self, event, character=None):
        character = character or self.character
        return Attendance.objects.create(
            player=character.player,
            event=event,
            character=character
        )

    def enter(self, event, influence_input, character=None):
        """Record a staff influence input for a character at an event."""
        character = character or self.character
        row, _ = CharacterEventInfluence.objects.get_or_create(
            event=event,
            character=character
        )
        row.influence_input = influence_input
        row.save(update_fields=['influence_input'])
        return row

    def refresh(self):
        self.character.refresh_from_db()
        return self.character
