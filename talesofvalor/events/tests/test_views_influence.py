"""Tests for the per event influence entry and processing screens."""
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from talesofvalor.characters.models import CharacterEventInfluence
from talesofvalor.characters.tests.base import InfluenceTestCase


class EventInfluenceViewTestCase(InfluenceTestCase):

    def setUp(self):
        super().setUp()
        self.staff.user_permissions.add(
            Permission.objects.get(codename='update_influence'),
            # the de facto "is staff" check used across the site.
            Permission.objects.get(codename='view_any_player')
        )
        self.nobody = User.objects.create_user(
            username='nobody',
            password='secret'
        )
        # influence is entered after a game, so the event being worked on
        # is one that has already happened.
        self.event = self.make_event("Spring 1", days_out=-10)
        self.attend(self.event)

    def login_staff(self):
        self.client.login(username='staff', password='secret')

    def grid_url(self):
        return reverse('events:influence_event', kwargs={'pk': self.event.pk})

    def process_url(self):
        return reverse('events:influence_process', kwargs={'pk': self.event.pk})

    def reverse_url(self):
        return reverse('events:influence_unprocess', kwargs={'pk': self.event.pk})

    def grid_post(self, row, influence_input):
        """Post the whole formset, the way the single save button does."""
        return self.client.post(self.grid_url(), {
            'influence_rows-TOTAL_FORMS': '1',
            'influence_rows-INITIAL_FORMS': '1',
            'influence_rows-MIN_NUM_FORMS': '0',
            'influence_rows-MAX_NUM_FORMS': '1000',
            'influence_rows-0-id': str(row.pk),
            'influence_rows-0-influence_input': str(influence_input),
            'influence_rows-0-notes': '',
        })


class EventInfluenceGridTest(EventInfluenceViewTestCase):

    def test_permission_is_required(self):
        response = self.client.get(self.grid_url())
        self.assertEqual(response.status_code, 302)

        self.client.login(username='nobody', password='secret')
        response = self.client.get(self.grid_url())
        self.assertEqual(response.status_code, 403)

    def test_staff_can_open_the_grid(self):
        self.login_staff()

        response = self.client.get(self.grid_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.character.name)

    def test_opening_the_grid_creates_a_row_per_attendee(self):
        self.login_staff()

        self.client.get(self.grid_url())
        self.client.get(self.grid_url())

        self.assertEqual(
            CharacterEventInfluence.objects.filter(event=self.event).count(), 1
        )

    def test_saving_records_input_without_moving_influence(self):
        """Typing numbers in is inert until the event is processed."""
        self.login_staff()
        self.client.get(self.grid_url())
        row = CharacterEventInfluence.objects.get(event=self.event)

        response = self.grid_post(row, 10)

        self.assertEqual(response.status_code, 302)
        row.refresh_from_db()
        self.assertEqual(row.influence_input, 10)
        self.assertIsNone(row.start_influence)
        self.assertEqual(self.refresh().influence, 0)


class EventInfluenceProcessViewTest(EventInfluenceViewTestCase):

    def test_processing_stamps_who_and_when(self):
        self.login_staff()
        self.enter(self.event, 10)

        response = self.client.post(self.process_url(), {'confirm': 'on'})

        self.assertEqual(response.status_code, 302)
        row = CharacterEventInfluence.objects.get(event=self.event)
        self.assertTrue(row.processed)
        self.assertEqual(row.processed_by, self.staff)
        self.assertEqual(self.refresh().influence, 6)

    def test_grid_refuses_edits_once_processed(self):
        self.login_staff()
        self.enter(self.event, 10)
        self.client.post(self.process_url(), {'confirm': 'on'})
        row = CharacterEventInfluence.objects.get(event=self.event)

        self.grid_post(row, 99)

        row.refresh_from_db()
        self.assertEqual(row.influence_input, 10)

    def test_reversing_puts_influence_back(self):
        self.login_staff()
        self.enter(self.event, 10)
        self.client.post(self.process_url(), {'confirm': 'on'})

        self.client.post(self.reverse_url(), {'confirm': 'on'})

        self.assertEqual(self.refresh().influence, 0)
        self.assertFalse(
            CharacterEventInfluence.objects.get(event=self.event).processed
        )

    def test_confirmation_is_required(self):
        self.login_staff()
        self.enter(self.event, 10)

        self.client.post(self.process_url(), {})

        self.assertFalse(
            CharacterEventInfluence.objects.get(event=self.event).processed
        )

    def test_permission_is_required_to_process(self):
        self.client.login(username='nobody', password='secret')
        self.enter(self.event, 10)

        response = self.client.post(self.process_url(), {'confirm': 'on'})

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            CharacterEventInfluence.objects.get(event=self.event).processed
        )
