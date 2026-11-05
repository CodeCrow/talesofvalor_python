"""
Tests for the PEL countdown in the page header.

The javascript only ticks whatever the server hands it, so what matters is
'pel_deadline' in the context processor: it decides whether there is a
countdown at all, and what moment it counts to.
"""
from datetime import date, time, timedelta

from cms.utils.permissions import set_current_user

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.utils import timezone

from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character
from talesofvalor.context_processors import pel_deadline
from talesofvalor.events.models import Event
from talesofvalor.players.models import PEL


class PELDeadlineContextTestCase(TestCase):
    """A player who attended an event whose PEL window is open."""

    def setUp(self):
        set_current_user(None)
        self.user = User.objects.create_user(
            username='player', first_name='Pat', last_name='Player',
            password='secret')
        self.player = self.user.player
        self.character = Character.objects.create(
            player=self.player, name="Aldric", active_flag=True)
        self.event = self.make_event(ended_days_ago=3, due_in_days=7)
        self.attend(self.event)

    def make_event(self, ended_days_ago, due_in_days, name="Spring 1"):
        event_date = date.today() - timedelta(days=ended_days_ago)
        return Event.objects.create(
            name=name,
            event_date=event_date,
            pel_due_date=date.today() + timedelta(days=due_in_days),
            bgs_due_date=event_date + timedelta(days=7)
        )

    def attend(self, event, character=None):
        return Attendance.objects.create(
            player=self.player,
            event=event,
            character=character or self.character
        )

    def context(self, user=None):
        request = RequestFactory().get('/')
        request.user = self.user if user is None else user
        return pel_deadline(request)


class WhenTheCountdownShowsTest(PELDeadlineContextTestCase):

    def test_it_shows_for_an_event_that_has_ended_and_is_not_overdue(self):
        context = self.context()

        self.assertIn('pel_deadline', context)
        self.assertEqual(context['pel_deadline_event'], self.event)

    def test_it_counts_to_the_end_of_the_due_day(self):
        """
        The deadline is a date, so the countdown runs to the last second of
        it -- the same rule the on time bonus uses.
        """
        due = self.context()['pel_deadline']

        self.assertEqual(timezone.localtime(due).date(), self.event.pel_due_date)
        self.assertEqual(timezone.localtime(due).time(), time(23, 59, 59))

    def test_nothing_once_the_due_date_has_passed(self):
        self.event.pel_due_date = date.today() - timedelta(days=1)
        self.event.save(update_fields=['pel_due_date'])

        self.assertEqual(self.context(), {})

    def test_nothing_while_the_event_is_still_running(self):
        """It only starts once the event is over."""
        self.event.event_date = date.today()
        self.event.save(update_fields=['event_date'])

        self.assertEqual(self.context(), {})

    def test_the_due_day_itself_still_counts(self):
        """Due today means there is still time left today, not zero."""
        self.event.pel_due_date = date.today()
        self.event.save(update_fields=['pel_due_date'])

        self.assertIn('pel_deadline', self.context())


class WhoSeesTheCountdownTest(PELDeadlineContextTestCase):

    def test_nothing_for_a_player_who_did_not_attend(self):
        Attendance.objects.all().delete()

        self.assertEqual(self.context(), {})

    def test_nothing_once_they_have_submitted(self):
        PEL.objects.create(
            character=self.character,
            event=self.event,
            submitted=timezone.now()
        )

        self.assertEqual(self.context(), {})

    def test_a_draft_is_not_enough_to_make_it_go_away(self):
        """A saved draft is still an outstanding PEL."""
        PEL.objects.create(character=self.character, event=self.event)

        self.assertIn('pel_deadline', self.context())

    def test_it_stays_while_another_character_still_owes_one(self):
        second = Character.objects.create(
            player=self.player, name="Brenna", active_flag=False)
        self.attend(self.event, character=second)
        PEL.objects.create(
            character=self.character,
            event=self.event,
            submitted=timezone.now()
        )

        self.assertIn('pel_deadline', self.context())

    def test_nothing_for_an_anonymous_visitor(self):
        from django.contrib.auth.models import AnonymousUser

        self.assertEqual(self.context(user=AnonymousUser()), {})


class WhichEventTheCountdownUsesTest(PELDeadlineContextTestCase):

    def test_the_most_recent_finished_event_wins(self):
        """
        With two events in their PEL window, the countdown belongs to the
        one that happened most recently.
        """
        older = self.make_event(
            ended_days_ago=30, due_in_days=2, name="Winter 1")
        self.attend(older)

        self.assertEqual(
            self.context()['pel_deadline_event'], self.event)


class TheCountdownRendersInThePageTest(PELDeadlineContextTestCase):
    """The box reaches the header, not just the context."""

    def test_the_header_carries_the_deadline(self):
        self.client.login(username='player', password='secret')

        response = self.client.get('/en/players/{}/'.format(self.player.id))

        self.assertContains(response, 'pel-countdown')
        self.assertContains(response, 'data-pel-deadline')

    def test_the_header_is_bare_once_submitted(self):
        PEL.objects.create(
            character=self.character,
            event=self.event,
            submitted=timezone.now()
        )
        self.client.login(username='player', password='secret')

        response = self.client.get('/en/players/{}/'.format(self.player.id))

        self.assertNotContains(response, 'pel-countdown')
