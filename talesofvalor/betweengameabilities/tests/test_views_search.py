"""
Tests for searching the text of between game ability questions and answers.

The search is staff only.  A player sees a BGA's answer only once
``answer_available`` is true, so letting them filter on answer text would
confirm words in an answer that is still being withheld -- which is why the
permission check lives in the view and not only in the template.
"""
from datetime import date, timedelta

from cms.utils.permissions import set_current_user

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from talesofvalor.attendance.models import Attendance
from talesofvalor.betweengameabilities.models import BetweenGameAbility
from talesofvalor.characters.models import Character
from talesofvalor.events.models import Event


class BGATextSearchTestCase(TestCase):
    """A staff user, a player with a character, and BGAs to search."""

    def setUp(self):
        # django-cms keeps the logged in user in a threadlocal that outlives
        # a test; left set, users created here get stamped as created by
        # somebody the previous test rolled back.
        set_current_user(None)

        self.staff = User.objects.create_user(
            username='staff', password='secret')
        self.staff.user_permissions.add(
            Permission.objects.get(codename='change_any_player'),
            Permission.objects.get(codename='view_any_player')
        )

        self.player_user = User.objects.create_user(
            username='player', password='secret')
        self.player = self.player_user.player
        self.character = Character.objects.create(
            player=self.player, name="Aldric", active_flag=True)

        # the list view falls back to the previous event, which has to be
        # comfortably in the past for 'previous_event' to find it.
        event_date = date.today() - timedelta(days=30)
        self.event = Event.objects.create(
            name="Spring 1",
            event_date=event_date,
            pel_due_date=event_date + timedelta(days=7),
            bgs_due_date=event_date + timedelta(days=7)
        )
        # non staff reach the list only for an event they attended.
        Attendance.objects.create(
            player=self.player, event=self.event, character=self.character)

        self.about_herbs = self.make_bga(
            question="<p>Can I brew a healing potion from marshwort?</p>",
            answer="<p>Yes, the marshwort steeps for a full day.</p>"
        )
        self.about_dragon = self.make_bga(
            question="<p>What do I learn about the northern road?</p>",
            answer="<p>A dragon was seen near the pass.</p>"
        )
        self.about_nothing = self.make_bga(
            question="<p>I spend the downtime resting.</p>",
            answer=""
        )

    def make_bga(self, question, answer, character=None):
        return BetweenGameAbility.objects.create(
            character=character or self.character,
            event=self.event,
            count=1,
            non_ability_source_flag=True,
            question=question,
            answer=answer
        )

    def search(self, text, **extra):
        """GET the list filtered by text, as the form submits it."""
        params = {'event_id': self.event.id, 'search_text': text}
        params.update(extra)
        return self.client.get(reverse(
            'betweengameabilities:betweengameability_list'), params)

    def ids_in(self, response):
        return {bga.id for bga in response.context['object_list']}


class StaffTextSearchTest(BGATextSearchTestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username='staff', password='secret')

    def test_matches_text_in_a_question(self):
        response = self.search("marshwort")

        self.assertEqual(self.ids_in(response), {self.about_herbs.id})

    def test_matches_text_in_an_answer(self):
        response = self.search("dragon")

        self.assertEqual(self.ids_in(response), {self.about_dragon.id})

    def test_search_is_case_insensitive(self):
        response = self.search("DRAGON")

        self.assertEqual(self.ids_in(response), {self.about_dragon.id})

    def test_separate_words_are_all_required(self):
        """
        Unquoted words are ANDed, and each may land in either field, so a
        term in the question and a term in the answer still match.
        """
        self.assertEqual(
            self.ids_in(self.search("marshwort steeps")),
            {self.about_herbs.id}
        )
        self.assertEqual(
            self.ids_in(self.search("marshwort dragon")),
            set()
        )

    def test_a_quoted_phrase_matches_a_run_of_words(self):
        self.assertEqual(
            self.ids_in(self.search('"healing potion"')),
            {self.about_herbs.id}
        )
        self.assertEqual(
            self.ids_in(self.search('"potion healing"')),
            set()
        )

    def test_no_match_returns_nothing(self):
        self.assertEqual(self.ids_in(self.search("basilisk")), set())

    def test_blank_search_does_not_filter(self):
        self.assertEqual(len(self.ids_in(self.search("   "))), 3)

    def test_search_composes_with_the_event_filter(self):
        """Searching must narrow the event's list, not replace the filter."""
        other_date = date.today() - timedelta(days=90)
        other_event = Event.objects.create(
            name="Winter 1",
            event_date=other_date,
            pel_due_date=other_date + timedelta(days=7),
            bgs_due_date=other_date + timedelta(days=7)
        )
        elsewhere = BetweenGameAbility.objects.create(
            character=self.character,
            event=other_event,
            count=1,
            non_ability_source_flag=True,
            question="<p>A dragon in winter.</p>",
            answer=""
        )

        response = self.search("dragon")

        ids = self.ids_in(response)
        self.assertIn(self.about_dragon.id, ids)
        self.assertNotIn(elsewhere.id, ids)


class PlayerCannotSearchTest(BGATextSearchTestCase):
    """
    A player must not be able to search, even by writing the query string
    by hand.  Hiding the input in the template is not the protection.
    """

    def setUp(self):
        super().setUp()
        self.client.login(username='player', password='secret')

    def test_the_search_input_is_not_rendered(self):
        response = self.client.get(
            reverse('betweengameabilities:betweengameability_list'),
            {'event_id': self.event.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="text"')

    def test_a_hand_written_text_query_is_ignored(self):
        """
        'dragon' appears only in an answer.  With the guard the list comes
        back unfiltered; without it, the player could tell which BGA holds
        the word while the answer itself is still hidden from them.
        """
        unfiltered = self.client.get(
            reverse('betweengameabilities:betweengameability_list'),
            {'event_id': self.event.id}
        )
        searched = self.search("dragon")

        self.assertEqual(self.ids_in(searched), self.ids_in(unfiltered))
        self.assertEqual(len(self.ids_in(searched)), 3)

    def test_a_player_still_only_sees_their_own(self):
        """The existing ownership filter is untouched by the search."""
        other_user = User.objects.create_user(
            username='other', password='secret')
        other_character = Character.objects.create(
            player=other_user.player, name="Brenna", active_flag=True)
        theirs = self.make_bga(
            question="<p>A dragon of my own.</p>",
            answer="",
            character=other_character
        )

        response = self.search("dragon")

        self.assertNotIn(theirs.id, self.ids_in(response))


class EventFilterTest(BGATextSearchTestCase):
    """
    How the event picker and the text search interact.

    A text search is meant to look across every event, so it deliberately
    skips the event narrowing.  Everything else still defaults to an event.
    """

    def setUp(self):
        super().setUp()
        self.client.login(username='staff', password='secret')
        older = date.today() - timedelta(days=120)
        self.older_event = Event.objects.create(
            name="Winter 1",
            event_date=older,
            pel_due_date=older + timedelta(days=7),
            bgs_due_date=older + timedelta(days=7)
        )
        self.in_winter = BetweenGameAbility.objects.create(
            character=self.character,
            event=self.older_event,
            count=1,
            non_ability_source_flag=True,
            question="<p>A dragon in winter.</p>",
            answer=""
        )

    def get(self, **params):
        return self.client.get(reverse(
            'betweengameabilities:betweengameability_list'), params)

    def test_the_picked_event_is_the_one_shown(self):
        """
        The chosen event has to survive dispatch.  It was briefly being
        overwritten by the previous event, so the heading and the dropdown
        disagreed with the list.
        """
        response = self.get(event_id=self.older_event.id)

        self.assertEqual(response.context['event'].id, self.older_event.id)

    def test_a_search_reaches_across_events(self):
        """The point of the search: do not confine it to one event."""
        response = self.get(search_text="dragon")

        ids = {bga.id for bga in response.context['object_list']}
        self.assertEqual(ids, {self.about_dragon.id, self.in_winter.id})

    def test_an_event_and_a_search_together_still_narrow(self):
        response = self.get(event_id=self.event.id, search_text="dragon")

        ids = {bga.id for bga in response.context['object_list']}
        self.assertEqual(ids, {self.about_dragon.id})

    def test_a_junk_event_id_does_not_break_the_page(self):
        """'?event_id=abc' used to raise ValueError out of the view."""
        response = self.get(event_id='abc')

        self.assertEqual(response.status_code, 200)

    def test_no_upcoming_event_still_lists(self):
        """
        Every event here is in the past, so there is no next event to
        default to.  That should leave the list alone rather than filtering
        it down to nothing.
        """
        self.assertIsNone(Event.next_event())

        response = self.get()

        self.assertGreater(len(response.context['object_list']), 0)


class SearchHighlightingTest(BGATextSearchTestCase):
    """The matched term is marked up in the list so the reader can see it."""

    def setUp(self):
        super().setUp()
        self.client.login(username='staff', password='secret')

    def test_a_match_in_a_question_is_marked(self):
        response = self.search("marshwort")

        self.assertContains(
            response, '<span class="highlight">marshwort</span>')

    def test_a_match_in_an_answer_is_marked(self):
        response = self.search("dragon")

        self.assertContains(
            response, '<span class="highlight">dragon</span>')

    def test_nothing_is_marked_without_a_search(self):
        response = self.client.get(reverse(
            'betweengameabilities:betweengameability_list'),
            {'event_id': self.event.id})

        self.assertNotContains(response, 'class="highlight"')

    def test_the_surrounding_markup_survives(self):
        """The stored question is HTML; marking must not disturb it."""
        response = self.search("marshwort")

        self.assertContains(
            response,
            '<p>Can I brew a healing potion from '
            '<span class="highlight">marshwort</span>?</p>'
        )


class PlayerSeesNoHighlightingTest(BGATextSearchTestCase):
    """
    A player cannot search, so nothing of theirs is ever marked -- including
    when they write 'search_text' into the query string by hand.
    """

    def setUp(self):
        super().setUp()
        self.client.login(username='player', password='secret')

    def test_a_hand_written_search_marks_nothing(self):
        response = self.search("potion")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="highlight"')


class AllEventsTest(BGATextSearchTestCase):
    """
    Choosing "All Events" has to stick.

    It is not the same as arriving with nothing chosen: opening the page
    cold still settles on an event, but asking for every event is a choice
    the page has to keep.
    """

    def setUp(self):
        super().setUp()
        self.client.login(username='staff', password='secret')
        older = date.today() - timedelta(days=120)
        self.older_event = Event.objects.create(
            name="Winter 1",
            event_date=older,
            pel_due_date=older + timedelta(days=7),
            bgs_due_date=older + timedelta(days=7)
        )
        self.in_winter = BetweenGameAbility.objects.create(
            character=self.character,
            event=self.older_event,
            count=1,
            non_ability_source_flag=True,
            question="<p>A question from winter.</p>",
            answer=""
        )

    def get(self, **params):
        return self.client.get(reverse(
            'betweengameabilities:betweengameability_list'), params)

    def test_all_events_lists_every_event(self):
        response = self.get(event_id=0)

        ids = {bga.id for bga in response.context['object_list']}
        self.assertIn(self.in_winter.id, ids)
        self.assertIn(self.about_herbs.id, ids)

    def test_all_events_leaves_the_heading_off(self):
        """The page used to fall back to showing the most recent event."""
        response = self.get(event_id=0)

        self.assertIsNone(response.context['event'])

    def test_all_events_stays_selected_in_the_picker(self):
        response = self.get(event_id=0)

        self.assertContains(
            response, '<option value="0" selected>All Events</option>',
            html=True
        )

    def test_all_events_survives_a_search(self):
        response = self.get(event_id=0, search_text="question")

        self.assertIsNone(response.context['event'])
        ids = {bga.id for bga in response.context['object_list']}
        self.assertIn(self.in_winter.id, ids)

    def test_choosing_an_event_still_shows_that_event(self):
        response = self.get(event_id=self.older_event.id)

        self.assertEqual(response.context['event'].id, self.older_event.id)
        ids = {bga.id for bga in response.context['object_list']}
        self.assertEqual(ids, {self.in_winter.id})

    def test_arriving_with_nothing_chosen_still_settles_on_an_event(self):
        """Opening the page cold is not the same as asking for all."""
        response = self.get()

        self.assertIsNotNone(response.context['event'])
