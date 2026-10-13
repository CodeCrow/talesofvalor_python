"""
Tests for the data migration that removes duplicate registrations.

The delete pass itself was verified against a clone of the production
database (1201 rows, 58 duplicated groups, 60 rows removed).  What is worth
pinning down here is the rule that picks which row of a group survives, since
that is the part carrying a judgement rather than a mechanism.
"""
import datetime
from importlib import import_module

from cms.utils.permissions import set_current_user

from django.contrib.auth.models import User
from django.test import TestCase

from talesofvalor.events.models import Event, EventRegistrationItem
from talesofvalor.players.models import Registration, RegistrationRequest

keep_score = import_module(
    'talesofvalor.players.migrations.0040_remove_duplicate_registrations'
).keep_score


class KeepScoreTest(TestCase):
    """
    Which of a group's duplicate rows should be kept.

    The rows are built but not saved: the unique constraint this migration
    clears the way for would reject them, and 'keep_score' only reads fields.
    """

    def setUp(self):
        set_current_user(None)
        self.user = User.objects.create_user(
            username='player1',
            password='notarealpassword'
        )
        self.event = Event.objects.create(
            name='Spring 1',
            event_date=datetime.date(2026, 4, 1),
            pel_due_date=datetime.date(2026, 4, 8),
            bgs_due_date=datetime.date(2026, 3, 1)
        )
        self.registration_item = EventRegistrationItem.objects.create(
            name='Single Event Pass',
            price=50
        )
        self.registration_item.events.set([self.event])
        self.registration_request = RegistrationRequest.objects.create(
            event_registration_item=self.registration_item,
            player=self.user.player,
            mealplan_flag=False,
            local_contact='555-0100'
        )

    def build(self, **overrides):
        """An unsaved registration copied off the request, then overridden."""
        values = dict(
            player=self.user.player,
            event=self.event,
            registration_request=self.registration_request,
            mealplan_flag=self.registration_request.mealplan_flag,
            local_contact=self.registration_request.local_contact
        )
        values.update(overrides)
        return Registration(**values)

    def test_row_agreeing_with_the_request_wins(self):
        """
        This is the real case from production: request 439 / event 17, where
        the two rows differed only on 'mealplan_flag' and the request settled
        it.
        """
        agrees = self.build()
        disagrees = self.build(mealplan_flag=True)
        self.assertGreater(keep_score(agrees), keep_score(disagrees))

    def test_hand_entered_notes_outrank_field_agreement(self):
        """A staff note must not be deleted to keep a tidier set of flags."""
        has_notes = self.build(mealplan_flag=True, notes='Arriving late Friday')
        agrees_but_bare = self.build()
        self.assertGreater(keep_score(has_notes), keep_score(agrees_but_bare))

    def test_hand_entered_cabin_outranks_field_agreement(self):
        has_cabin = self.build(mealplan_flag=True, cabin='Birch')
        agrees_but_bare = self.build()
        self.assertGreater(keep_score(has_cabin), keep_score(agrees_but_bare))

    def test_whitespace_is_not_hand_entered_data(self):
        blank = self.build(cabin='   ', notes='\n')
        bare = self.build()
        self.assertEqual(keep_score(blank), keep_score(bare))

    def test_identical_rows_score_the_same(self):
        """
        57 of the 58 production groups were identical, so the rule has to fall
        through to something deterministic rather than preferring either row.
        """
        self.assertEqual(keep_score(self.build()), keep_score(self.build()))
