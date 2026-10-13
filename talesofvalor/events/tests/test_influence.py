"""
Tests for rolling influence forward across an event.

Influence carries between events: a character's current influence is the end
of game total from the last processed event, and processing an event rolls
everyone forward from there.
"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from talesofvalor.characters.models import (
    DEFAULT_INFLUENCE_CHANGE,
    Character,
    CharacterEventInfluence,
    CorruptionLevel,
)
from talesofvalor.characters.tests.base import InfluenceTestCase
from talesofvalor.events.services.influence import (
    ensure_event_rows,
    has_later_processing,
    process_event_influence,
    unprocess_event_influence,
)


class ProcessEventInfluenceTest(InfluenceTestCase):

    def test_first_event_starts_from_zero(self):
        """A character with no history starts at zero and rolls forward."""
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)

        counts = process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(event=event, character=self.character)
        self.assertEqual(row.start_influence, 0)
        self.assertEqual(row.end_influence, 10 + DEFAULT_INFLUENCE_CHANGE)
        self.assertTrue(row.corruption_flag)
        self.assertEqual(self.refresh().influence, 6)
        self.assertEqual(counts['processed'], 1)
        self.assertEqual(counts['flagged'], 1)

    def test_roll_forward_uses_previous_end(self):
        """The second event starts where the first ended, and losing does not flag."""
        first = self.make_event("Spring 1", days_out=-30)
        self.attend(first)
        self.enter(first, 10)
        process_event_influence(first, self.staff)

        second = self.make_event("Spring 2", days_out=-10)
        self.attend(second)
        self.enter(second, 8)
        process_event_influence(second, self.staff)

        row = CharacterEventInfluence.objects.get(event=second, character=self.character)
        self.assertEqual(row.start_influence, 6)
        self.assertEqual(row.end_influence, 4)
        self.assertFalse(row.corruption_flag)
        self.assertEqual(self.refresh().influence, 4)

    def test_influence_change_floors_at_zero(self):
        """Influence never goes negative, however small the input."""
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 2)

        process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(event=event, character=self.character)
        self.assertEqual(row.end_influence, 0)
        self.assertEqual(self.refresh().influence, 0)

    def test_corruption_flag_is_strict(self):
        """Holding steady is not a gain, so it does not flag."""
        first = self.make_event("Spring 1", days_out=-30)
        self.attend(first)
        self.enter(first, 10)
        process_event_influence(first, self.staff)
        self.assertEqual(self.refresh().influence, 6)

        # an input of 10 again lands back on exactly 6.
        second = self.make_event("Spring 2", days_out=-10)
        self.attend(second)
        self.enter(second, 10)
        process_event_influence(second, self.staff)

        row = CharacterEventInfluence.objects.get(event=second, character=self.character)
        self.assertEqual(row.start_influence, row.end_influence)
        self.assertFalse(row.corruption_flag)

    def test_rows_without_input_are_skipped(self):
        """A character with no data entered is left completely alone."""
        event = self.make_event("Spring 1")
        self.attend(event)
        ensure_event_rows(event)

        counts = process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(event=event, character=self.character)
        self.assertIsNone(row.start_influence)
        self.assertIsNone(row.processed_at)
        self.assertEqual(self.refresh().influence, 0)
        self.assertEqual(counts['skipped'], 1)
        self.assertEqual(counts['processed'], 0)

    def test_processing_twice_does_not_double_apply(self):
        """Re-running processing is harmless."""
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)

        process_event_influence(event, self.staff)
        counts = process_event_influence(event, self.staff)

        self.assertEqual(self.refresh().influence, 6)
        self.assertEqual(counts['processed'], 0)

    def test_processing_is_refused_out_of_order(self):
        """An earlier event cannot be processed once a later one has been."""
        earlier = self.make_event("Spring 1", days_out=-30)
        later = self.make_event("Spring 2", days_out=-10)
        self.attend(earlier)
        self.attend(later)
        self.enter(earlier, 10)
        self.enter(later, 10)

        process_event_influence(later, self.staff)

        self.assertTrue(has_later_processing(earlier))
        with self.assertRaises(ValidationError):
            process_event_influence(earlier, self.staff)


class CorruptionDuringProcessingTest(InfluenceTestCase):

    def test_processing_survives_an_empty_ladder(self):
        """Flagged but unlevelled is a legitimate state, not an error."""
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)

        process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(event=event, character=self.character)
        self.assertTrue(row.corruption_flag)
        self.assertIsNone(row.corruption_level)

    def test_level_is_resolved_from_end_influence(self):
        """The level comes off the changed value, not the raw input."""
        CorruptionLevel.objects.create(name="Tainted", threshold=6)
        CorruptionLevel.objects.create(name="Marked", threshold=10)
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)

        process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(event=event, character=self.character)
        self.assertEqual(row.corruption_level.name, "Tainted")

    def test_an_unflagged_character_gets_no_level(self):
        CorruptionLevel.objects.create(name="Tainted", threshold=0)
        first = self.make_event("Spring 1", days_out=-30)
        self.attend(first)
        self.enter(first, 20)
        process_event_influence(first, self.staff)

        second = self.make_event("Spring 2", days_out=-10)
        self.attend(second)
        self.enter(second, 8)
        process_event_influence(second, self.staff)

        row = CharacterEventInfluence.objects.get(event=second, character=self.character)
        self.assertFalse(row.corruption_flag)
        self.assertIsNone(row.corruption_level)


class UnprocessEventInfluenceTest(InfluenceTestCase):

    def test_unprocess_restores_the_previous_value(self):
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)
        process_event_influence(event, self.staff)

        unprocess_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(event=event, character=self.character)
        self.assertEqual(self.refresh().influence, 0)
        self.assertIsNone(row.start_influence)
        self.assertIsNone(row.end_influence)
        self.assertFalse(row.corruption_flag)
        self.assertFalse(row.processed)

    def test_unprocess_keeps_the_input_for_reprocessing(self):
        """Staff fix a typo and run it again without retyping everything."""
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)
        process_event_influence(event, self.staff)
        unprocess_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(event=event, character=self.character)
        self.assertEqual(row.influence_input, 10)

        row.influence_input = 20
        row.save(update_fields=['influence_input'])
        process_event_influence(event, self.staff)
        self.assertEqual(self.refresh().influence, 16)

    def test_unprocess_is_safe_after_a_manual_adjustment(self):
        """
        Reversal unwinds its own change rather than restoring the old value,
        so an adjustment made after processing is not silently lost.
        """
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)
        process_event_influence(event, self.staff)
        self.assertEqual(self.refresh().influence, 6)

        self.character.apply_influence(5, self.staff, "found a patron")
        self.assertEqual(self.refresh().influence, 11)

        unprocess_event_influence(event, self.staff)

        # the +6 from processing is undone, the +5 adjustment survives.
        self.assertEqual(self.refresh().influence, 5)


class ManualAdjustmentBetweenEventsTest(InfluenceTestCase):

    def test_adjustment_carries_into_the_next_start(self):
        """Influence gained between games is where the next event starts."""
        first = self.make_event("Spring 1", days_out=-30)
        self.attend(first)
        self.enter(first, 10)
        process_event_influence(first, self.staff)

        self.character.apply_influence(3, self.staff, "between game scheming")

        second = self.make_event("Spring 2", days_out=-10)
        self.attend(second)
        self.enter(second, 12)
        process_event_influence(second, self.staff)

        row = CharacterEventInfluence.objects.get(event=second, character=self.character)
        self.assertEqual(row.start_influence, 9)


class EventRowsTest(InfluenceTestCase):

    def test_rows_are_created_for_attendees(self):
        event = self.make_event("Spring 1")
        self.attend(event)

        rows = ensure_event_rows(event)

        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows.first().character, self.character)

    def test_rows_are_not_created_for_absentees(self):
        """Registration is not attendance; only people who showed up count."""
        event = self.make_event("Spring 1")

        rows = ensure_event_rows(event)

        self.assertEqual(rows.count(), 0)

    def test_ensure_rows_is_idempotent(self):
        event = self.make_event("Spring 1")
        self.attend(event)

        ensure_event_rows(event)
        ensure_event_rows(event)

        self.assertEqual(
            CharacterEventInfluence.objects.filter(event=event).count(), 1
        )

    def test_duplicate_attendance_yields_one_row(self):
        """Attendance has no unique constraint, so duplicates are possible."""
        event = self.make_event("Spring 1")
        self.attend(event)
        self.attend(event)

        rows = ensure_event_rows(event)

        self.assertEqual(rows.count(), 1)


class CharacterInfluenceChangeTest(InfluenceTestCase):
    """
    Processing an event with a character on their own influence change.

    Most characters lose the usual amount.  Staff can give a character a
    different signed change, which is used in its place at every event.
    """

    def set_change(self, value, character=None):
        character = character or self.character
        character.influence_change = value
        character.save(update_fields=['influence_change'])
        return character

    def test_a_bigger_loss_is_applied(self):
        self.set_change(-7)
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)

        process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(
            event=event, character=self.character)
        self.assertEqual(row.end_influence, 3)
        self.assertEqual(self.refresh().influence, 3)

    def test_a_gain_is_applied(self):
        """A positive change adds influence rather than taking it away."""
        self.set_change(2)
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)

        process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(
            event=event, character=self.character)
        self.assertEqual(row.end_influence, 12)
        self.assertEqual(self.refresh().influence, 12)

    def test_zero_leaves_the_input_alone(self):
        self.set_change(0)
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)

        process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(
            event=event, character=self.character)
        self.assertEqual(row.end_influence, 10)

    def test_a_big_loss_still_floors_at_zero(self):
        self.set_change(-20)
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 5)

        process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(
            event=event, character=self.character)
        self.assertEqual(row.end_influence, 0)
        self.assertEqual(self.refresh().influence, 0)

    def test_only_the_character_with_their_own_change_is_affected(self):
        """Everyone else at the event still uses the usual amount."""
        other_user = User.objects.create_user(
            username='other', password='secret')
        other = Character.objects.create(
            player=other_user.player,
            name="Brenna",
            active_flag=True
        )
        self.set_change(-7)
        event = self.make_event("Spring 1")
        self.attend(event)
        self.attend(event, character=other)
        self.enter(event, 10)
        self.enter(event, 10, character=other)

        process_event_influence(event, self.staff)

        mine = CharacterEventInfluence.objects.get(
            event=event, character=self.character)
        theirs = CharacterEventInfluence.objects.get(
            event=event, character=other)
        self.assertEqual(mine.end_influence, 3)
        self.assertEqual(theirs.end_influence, 10 + DEFAULT_INFLUENCE_CHANGE)

    def test_a_gain_flags_corruption(self):
        """
        Gaining influence is what flags a corruption, so a positive change
        on its own is enough to flag a character who held steady.
        """
        self.set_change(2)
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 0)

        process_event_influence(event, self.staff)

        row = CharacterEventInfluence.objects.get(
            event=event, character=self.character)
        self.assertEqual(row.end_influence, 2)
        self.assertTrue(row.corruption_flag)

    def test_reversal_undoes_the_change(self):
        """
        A reversal unwinds the stored delta, so it has to come back to where
        it started whatever change was applied.
        """
        self.set_change(-7)
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)
        process_event_influence(event, self.staff)
        self.assertEqual(self.refresh().influence, 3)

        unprocess_event_influence(event, self.staff)

        self.assertEqual(self.refresh().influence, 0)

    def test_a_change_set_after_processing_does_not_rewrite_history(self):
        """
        The start and end are stored when the event is processed, so giving a
        character their own change afterwards must not disturb an event that
        has already rolled forward.
        """
        event = self.make_event("Spring 1")
        self.attend(event)
        self.enter(event, 10)
        process_event_influence(event, self.staff)

        self.set_change(-7)

        row = CharacterEventInfluence.objects.get(
            event=event, character=self.character)
        self.assertEqual(row.end_influence, 10 + DEFAULT_INFLUENCE_CHANGE)
        self.assertEqual(self.refresh().influence, 6)
