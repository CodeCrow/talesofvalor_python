"""
Tests for the player models.
"""
import datetime

from cms.utils.permissions import set_current_user

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings

from talesofvalor.events.models import Event, EventRegistrationItem
from talesofvalor.players.models import COMPLETE, REQUESTED, \
    Registration, RegistrationRequest


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class RequestCompleteTest(TestCase):
    """
    'RegistrationRequest.request_complete' has four callers, two of which fire
    on a GET, so it has to be safe to call repeatedly.
    """

    def setUp(self):
        # django-cms remembers the logged in user in a threadlocal that
        # outlives a test.  Left set, the user created below would be
        # stamped as created by somebody the previous test rolled back.
        set_current_user(None)
        # creating a User creates the attached Player through a post_save
        # receiver, so take the player from the user.
        self.user = User.objects.create_user(
            username='player1',
            first_name='Test',
            last_name='Player',
            password='notarealpassword'
        )
        self.registration_item = EventRegistrationItem.objects.create(
            name='Season Pass',
            price=100
        )
        self.events = [
            Event.objects.create(
                name='Spring {}'.format(index),
                # 'Registration.save' looks up earlier registrations by event
                # date, so each event needs a real, distinct date.
                event_date=datetime.date(2026, 4, index),
                pel_due_date=datetime.date(2026, 4, index + 7),
                bgs_due_date=datetime.date(2026, 3, index)
            )
            for index in (1, 2)
        ]
        self.registration_item.events.set(self.events)
        self.registration_request = RegistrationRequest.objects.create(
            event_registration_item=self.registration_item,
            player=self.user.player
        )
        self.request = RequestFactory().get(
            '/registration/request/{}/alreadypaid/'.format(
                self.registration_request.id
            )
        )

    def complete(self):
        """Run the method under test the way the views do."""
        RegistrationRequest.request_complete(
            self.registration_request.id,
            self.user,
            self.request
        )

    def registrations(self):
        return Registration.objects.filter(
            registration_request=self.registration_request
        )

    def test_creates_one_registration_per_event(self):
        self.complete()
        self.assertEqual(self.registrations().count(), 2)
        self.assertEqual(
            set(self.registrations().values_list('event', flat=True)),
            {event.id for event in self.events}
        )

    def test_marks_request_complete(self):
        self.assertEqual(self.registration_request.status, REQUESTED)
        self.complete()
        self.registration_request.refresh_from_db()
        self.assertEqual(self.registration_request.status, COMPLETE)

    def test_called_twice_creates_no_duplicates(self):
        """A reloaded GET must not register the player a second time."""
        self.complete()
        self.complete()
        self.assertEqual(self.registrations().count(), 2)
        self.registration_request.refresh_from_db()
        self.assertEqual(self.registration_request.status, COMPLETE)

    def test_second_call_is_logged(self):
        self.complete()
        LogEntry.objects.all().delete()
        self.complete()
        log_entry = LogEntry.objects.get()
        self.assertIn(
            'Duplicate registration suppressed',
            log_entry.change_message
        )
        self.assertEqual(
            int(log_entry.object_id),
            self.registration_request.id
        )

    def test_duplicate_email_carries_no_request_dump(self):
        """
        The duplicate notice used to mail a dump of the whole request, cookies
        and auth headers included.
        """
        self.complete()
        mail.outbox = []
        self.complete()
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertIn('Duplicate registration suppressed', body)
        self.assertNotIn('HTTP_COOKIE', body)
        self.assertNotIn('csrftoken', body)
        self.assertNotIn('sessionid', body)

    def test_survives_a_preexisting_duplicate(self):
        """
        Rows duplicated before the constraint existed made the old '.get()'
        raise MultipleObjectsReturned.
        """
        self.complete()
        Registration.objects.filter(event=self.events[0]).update(
            registration_request=None
        )
        Registration.objects.create(
            player=self.user.player,
            event=self.events[0],
            registration_request=None
        )
        # the request is already COMPLETE, so this short circuits rather than
        # tripping over the pair of rows.
        self.complete()
        self.assertEqual(
            Registration.objects.filter(event=self.events[0]).count(),
            2
        )

    def test_failure_leaves_the_request_retryable(self):
        """
        The status used to be saved first, so a failure half way through left
        the player with a COMPLETE request and no registrations.
        """
        broken_request = RequestFactory().get('/')
        # 'build_absolute_uri' is called while building the staff notification;
        # make it explode to stand in for any mid-flight failure.
        broken_request.build_absolute_uri = None
        with self.assertRaises(TypeError):
            RegistrationRequest.request_complete(
                self.registration_request.id,
                self.user,
                broken_request
            )
        self.registration_request.refresh_from_db()
        self.assertEqual(self.registration_request.status, REQUESTED)
        self.assertEqual(self.registrations().count(), 0)
