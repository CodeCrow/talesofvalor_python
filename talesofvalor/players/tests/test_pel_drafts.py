"""
Tests for saving a PEL as a draft and submitting it later.

A PEL used to be written in one sitting: creating the row awarded the on
time bonus, logged it, and mailed the staff.  All three now hang off the
submission instead, so a player can save a half finished letter without any
of it happening.

'submitted' carries the state: empty means draft.
"""
from datetime import date, timedelta

from cms.utils.permissions import set_current_user

from django.contrib.auth.models import Permission, User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character
from talesofvalor.events.models import Event
from talesofvalor.players.models import PEL


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class PELDraftTestCase(TestCase):
    """A player with a character who attended an event they can write up."""

    # the event is in the past and its PEL deadline has not passed, so a
    # submission now counts as on time unless a test says otherwise.
    DAYS_AGO = 10
    DUE_IN = 5

    def setUp(self):
        # django-cms keeps the logged in user in a threadlocal that outlives
        # a test; left set, users created here are stamped as created by
        # somebody the previous test rolled back.
        set_current_user(None)
        self.player_user = User.objects.create_user(
            username='player',
            first_name='Pat',
            last_name='Player',
            password='secret'
        )
        self.player = self.player_user.player
        self.character = Character.objects.create(
            player=self.player, name="Aldric", active_flag=True)

        event_date = date.today() - timedelta(days=self.DAYS_AGO)
        self.event = Event.objects.create(
            name="Spring 1",
            event_date=event_date,
            pel_due_date=date.today() + timedelta(days=self.DUE_IN),
            bgs_due_date=event_date + timedelta(days=7)
        )
        Attendance.objects.create(
            player=self.player, event=self.event, character=self.character)

        self.staff = User.objects.create_user(
            username='staff', password='secret')
        self.staff.user_permissions.add(
            Permission.objects.get(codename='view_any_player'),
            Permission.objects.get(codename='change_any_player')
        )

    def create_url(self):
        return reverse('players:pel_create', kwargs={
            'character_id': self.character.id,
            'event_id': self.event.id
        })

    def post_new(self, button, **extra):
        """Fill in the create form and press one of the two buttons."""
        data = {
            'character': self.character.id,
            'event': self.event.id,
            'return_url': '/',
            'rating': 4,
            'favorites': 'the woods',
            button: 'x',
        }
        data.update(extra)
        return self.client.post(self.create_url(), data)

    def cp(self):
        self.player.refresh_from_db()
        return self.player.cp_available


class SavingADraftTest(PELDraftTestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username='player', password='secret')

    def test_saving_a_draft_does_not_mark_it_submitted(self):
        self.post_new('save_draft')

        pel = PEL.objects.get()
        self.assertIsNone(pel.submitted)

    def test_saving_a_draft_awards_no_cp(self):
        before = self.cp()

        self.post_new('save_draft')

        self.assertEqual(self.cp(), before)

    def test_saving_a_draft_tells_nobody(self):
        self.post_new('save_draft')

        self.assertEqual(len(mail.outbox), 0)

    def test_the_draft_keeps_what_was_typed(self):
        self.post_new('save_draft', favorites='the standing stones')

        self.assertEqual(PEL.objects.get().favorites, 'the standing stones')


class SubmittingTest(PELDraftTestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username='player', password='secret')

    def test_submitting_stamps_the_time(self):
        self.post_new('submit_pel')

        self.assertIsNotNone(PEL.objects.get().submitted)

    def test_submitting_on_time_awards_the_bonus(self):
        before = self.cp()

        self.post_new('submit_pel')

        self.assertEqual(self.cp(), before + PEL.ON_TIME_BONUS)

    def test_submitting_mails_the_staff_once(self):
        self.post_new('submit_pel')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('submitted a PEL', mail.outbox[0].body)

    def test_a_draft_submitted_late_earns_nothing(self):
        """
        On time is measured at submission, so sitting on a finished letter
        past the deadline does not still pay.
        """
        self.event.pel_due_date = date.today() - timedelta(days=1)
        self.event.save(update_fields=['pel_due_date'])
        before = self.cp()

        self.post_new('submit_pel')

        self.assertIsNotNone(PEL.objects.get().submitted)
        self.assertEqual(self.cp(), before)

    def test_saving_then_submitting_awards_the_bonus_once(self):
        """The draft save must not pay, and the submission must pay once."""
        before = self.cp()
        self.post_new('save_draft')
        self.assertEqual(self.cp(), before)
        pel = PEL.objects.get()

        self.client.post(
            reverse('players:pel_update', kwargs={'pk': pel.id}),
            {
                'character': self.character.id,
                'event': self.event.id,
                'return_url': '/',
                'rating': 4,
                'submit_pel': 'x',
            }
        )

        pel.refresh_from_db()
        self.assertIsNotNone(pel.submitted)
        self.assertEqual(self.cp(), before + PEL.ON_TIME_BONUS)
        self.assertEqual(len(mail.outbox), 1)


class SubmittedIsReadOnlyForThePlayerTest(PELDraftTestCase):
    """
    Submitting hands the letter over.  The player cannot edit it after that,
    and the staff still can.
    """

    def setUp(self):
        super().setUp()
        self.pel = PEL.objects.create(
            character=self.character, event=self.event)

    def update_url(self):
        return reverse('players:pel_update', kwargs={'pk': self.pel.id})

    def test_a_player_can_edit_their_draft(self):
        self.client.login(username='player', password='secret')

        self.assertEqual(self.client.get(self.update_url()).status_code, 200)

    def test_a_player_cannot_edit_it_once_submitted(self):
        self.pel.submitted = timezone.now()
        self.pel.save(update_fields=['submitted'])
        self.client.login(username='player', password='secret')

        self.assertEqual(self.client.get(self.update_url()).status_code, 403)

    def test_staff_can_still_edit_a_submitted_pel(self):
        self.pel.submitted = timezone.now()
        self.pel.save(update_fields=['submitted'])
        self.client.login(username='staff', password='secret')

        self.assertEqual(self.client.get(self.update_url()).status_code, 200)

    def test_the_redirect_sends_a_submitted_pel_to_the_read_only_page(self):
        """
        The redirect used to always aim at the edit form, which would now be
        a 403 for the player who wrote it.
        """
        self.pel.submitted = timezone.now()
        self.pel.save(update_fields=['submitted'])
        self.client.login(username='player', password='secret')

        response = self.client.get(reverse('players:pel_redirect', kwargs={
            'character_id': self.character.id,
            'event_id': self.event.id
        }))

        self.assertEqual(
            response.url,
            reverse('players:pel_detail', kwargs={'pk': self.pel.id})
        )

    def test_the_redirect_sends_a_draft_to_the_form(self):
        self.client.login(username='player', password='secret')

        response = self.client.get(reverse('players:pel_redirect', kwargs={
            'character_id': self.character.id,
            'event_id': self.event.id
        }))

        self.assertEqual(
            response.url,
            reverse('players:pel_update', kwargs={'pk': self.pel.id})
        )


class StaffListExcludesDraftsTest(PELDraftTestCase):

    def setUp(self):
        super().setUp()
        self.draft = PEL.objects.create(
            character=self.character, event=self.event)
        other_date = date.today() - timedelta(days=60)
        other_event = Event.objects.create(
            name="Winter 1",
            event_date=other_date,
            pel_due_date=other_date + timedelta(days=7),
            bgs_due_date=other_date + timedelta(days=7)
        )
        self.sent = PEL.objects.create(
            character=self.character,
            event=other_event,
            submitted=timezone.now()
        )
        self.client.login(username='staff', password='secret')

    def test_the_list_shows_only_submitted_pels(self):
        response = self.client.get(reverse('players:pel_list'))

        ids = {pel.id for pel in response.context['object_list']}
        self.assertIn(self.sent.id, ids)
        self.assertNotIn(self.draft.id, ids)


class DraftsDoNotGrantHeavyArmorTest(PELDraftTestCase):
    """
    'Character.skillhash' grants the Heavy Armor skill above four PELs with
    the flag set.  A draft must not count, or someone could tick the box and
    take the cheaper prerequisite without ever sending the letter.
    """

    def make_pels(self, count, submitted):
        for index in range(count):
            event_date = date.today() - timedelta(days=100 + index)
            event = Event.objects.create(
                name="Event {}".format(index),
                event_date=event_date,
                pel_due_date=event_date + timedelta(days=7),
                bgs_due_date=event_date + timedelta(days=7)
            )
            PEL.objects.create(
                character=self.character,
                event=event,
                heavy_armor_worn_flag=True,
                submitted=timezone.now() if submitted else None
            )

    def counted(self):
        return PEL.objects.filter(
            character=self.character,
            heavy_armor_worn_flag=True,
            submitted__isnull=False
        ).count()

    def test_drafts_are_not_counted(self):
        self.make_pels(5, submitted=False)

        self.assertEqual(self.counted(), 0)

    def test_submitted_ones_are_counted(self):
        self.make_pels(5, submitted=True)

        self.assertEqual(self.counted(), 5)
