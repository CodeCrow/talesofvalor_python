"""
Tests for the corruption filter and column on the character list.

A character counts as corrupted when their influence has reached the lowest
rung of the ladder staff maintain in the admin.  Both the checkbox and the
column use that one test, so they cannot disagree.

Neither is for players: they are behind 'players.view_any_player', the
permission this codebase already treats as "can edit any character".
"""
from cms.utils.permissions import set_current_user

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from talesofvalor.characters.models import Character, CorruptionLevel


class CorruptionListTestCase(TestCase):

    def setUp(self):
        set_current_user(None)
        self.staff = User.objects.create_user(
            username='staff', password='secret')
        self.staff.user_permissions.add(
            Permission.objects.get(codename='view_any_player'))
        self.player_user = User.objects.create_user(
            username='player', password='secret')

        # influence 9 and 3, with the lowest rung at 5
        self.corrupted = self.make_character('Tainted', 9)
        self.clean = self.make_character('Pure', 3)
        CorruptionLevel.objects.create(name='Marked', threshold=5)
        CorruptionLevel.objects.create(name='Lost', threshold=20)

    def make_character(self, name, influence, user=None):
        owner = user or self.player_user
        return Character.objects.create(
            player=owner.player, name=name,
            influence=influence, active_flag=False)

    def listing(self, **params):
        return self.client.get(reverse('characters:character_list'), params)

    def names(self, response):
        return {c.name for c in response.context['object_list']}


class TheFilterTest(CorruptionListTestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username='staff', password='secret')

    def test_unfiltered_shows_everyone(self):
        names = self.names(self.listing(search='search'))

        self.assertIn('Tainted', names)
        self.assertIn('Pure', names)

    def test_the_checkbox_narrows_to_corrupted_characters(self):
        names = self.names(self.listing(search='search', corrupted='1'))

        self.assertEqual(names, {'Tainted'})

    def test_a_character_exactly_on_the_rung_counts(self):
        """The threshold is inclusive: reaching it is enough."""
        self.make_character('Borderline', 5)

        names = self.names(self.listing(search='search', corrupted='1'))

        self.assertIn('Borderline', names)

    def test_the_lowest_rung_is_what_matters_not_the_highest(self):
        """
        There are two rungs, at 5 and 20.  A character on 9 has reached the
        ladder even though they are nowhere near the top of it.
        """
        names = self.names(self.listing(search='search', corrupted='1'))

        self.assertIn('Tainted', names)

    def test_with_no_ladder_configured_nobody_is_corrupted(self):
        CorruptionLevel.objects.all().delete()

        response = self.listing(search='search', corrupted='1')

        self.assertEqual(self.names(response), {'Tainted', 'Pure'})
        self.assertFalse(response.context['corruption_configured'])


class TheColumnTest(CorruptionListTestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username='staff', password='secret')

    def test_the_column_is_labelled(self):
        self.assertContains(self.listing(), 'Corrupted')

    def test_a_corrupted_character_is_marked(self):
        response = self.listing()

        self.assertContains(response, 'corrupted-mark')

    def test_the_annotation_matches_the_filter(self):
        """
        The column and the checkbox must agree, or the page contradicts
        itself.
        """
        by_annotation = {
            c.name for c in self.listing().context['object_list']
            if c.is_corrupted
        }
        by_filter = self.names(self.listing(search='search', corrupted='1'))

        self.assertEqual(by_annotation, by_filter)

    def test_the_mark_is_absent_with_no_ladder(self):
        CorruptionLevel.objects.all().delete()

        self.assertNotContains(self.listing(), 'corrupted-mark')


class OnlyStaffSeeItTest(CorruptionListTestCase):

    def test_a_player_sees_neither_the_checkbox_nor_the_column(self):
        self.client.login(username='player', password='secret')

        response = self.listing()

        self.assertNotContains(response, 'name="corrupted"')
        self.assertNotContains(response, 'corrupted-mark')
        self.assertNotContains(response, '<th>Corrupted</th>', html=False)

    def test_a_player_cannot_filter_by_writing_the_query_string(self):
        """
        The filter narrows the list, so a player using it would learn which
        characters are corrupted without ever seeing the column.
        """
        self.client.login(username='player', password='secret')

        names = self.names(self.listing(search='search', corrupted='1'))

        self.assertEqual(names, {'Tainted', 'Pure'})

    def test_staff_do_see_both(self):
        self.client.login(username='staff', password='secret')

        response = self.listing()

        self.assertContains(response, 'name="corrupted"')
        self.assertContains(response, 'corrupted-mark')
