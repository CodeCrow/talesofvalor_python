"""Tests for the per character influence screens."""
from django.contrib.auth.models import Permission, User
from django.urls import reverse

from talesofvalor.players.models import Registration

from .base import InfluenceTestCase


class CharacterInfluenceViewTestCase(InfluenceTestCase):

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

    def login_staff(self):
        self.client.login(username='staff', password='secret')


class CharacterInfluenceAdjustViewTest(CharacterInfluenceViewTestCase):

    def url(self):
        return reverse(
            'characters:influence_adjust', kwargs={'pk': self.character.pk})

    def test_permission_is_required(self):
        self.client.login(username='nobody', password='secret')

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 403)

    def test_adjustment_changes_influence(self):
        self.login_staff()

        response = self.client.post(self.url(), {
            'delta': '5',
            'reason': 'found a patron',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.refresh().influence, 5)

    def test_a_negative_adjustment_is_allowed(self):
        self.login_staff()
        self.character.apply_influence(10, self.staff, "an event")

        self.client.post(self.url(), {
            'delta': '-4',
            'reason': 'a debt came due',
        })

        self.assertEqual(self.refresh().influence, 6)

    def test_zero_adjustment_is_rejected(self):
        self.login_staff()

        response = self.client.post(self.url(), {
            'delta': '0',
            'reason': 'nothing happened',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.refresh().influence, 0)


class CharacterInfluenceHistoryViewTest(CharacterInfluenceViewTestCase):

    def url(self):
        return reverse(
            'characters:influence_history', kwargs={'pk': self.character.pk})

    def test_a_player_can_see_their_own_history(self):
        self.client.login(username='player', password='secret')

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 200)

    def test_another_player_cannot(self):
        self.client.login(username='nobody', password='secret')

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 403)

    def test_staff_can_see_anyone(self):
        self.login_staff()

        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 200)


class StartingInfluenceDisplayTest(CharacterInfluenceViewTestCase):

    def test_starting_influence_shows_on_detail_and_print(self):
        """
        The same partial feeds the detail page and the printed sheet, so the
        value players read off their next character sheet comes from here.
        """
        self.login_staff()
        event = self.make_event("Spring 1", days_out=-10)
        self.attend(event)
        self.enter(event, 10)
        self.client.post(
            reverse('events:influence_process', kwargs={'pk': event.pk}),
            {'confirm': 'on'}
        )

        detail = self.client.get(
            reverse('characters:character_detail', kwargs={'pk': self.character.pk})
        )
        self.assertContains(detail, "Starting Influence: 6")

        # the print list is the sheets for the next event, built from who
        # has registered for it.
        next_event = self.make_event("Spring 2", days_out=30)
        Registration.objects.create(player=self.player, event=next_event)
        printed = self.client.get(reverse('characters:character_print_list'))
        self.assertContains(printed, "Starting Influence: 6")
