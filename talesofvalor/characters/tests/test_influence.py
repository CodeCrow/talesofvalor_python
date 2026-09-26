"""
Tests for influence on a single character.

Rolling a whole event forward is covered in ``events.tests.test_influence``.
"""
from talesofvalor.characters.models import CorruptionLevel

from .base import InfluenceTestCase


class ApplyInfluenceTest(InfluenceTestCase):

    def test_influence_is_added(self):
        applied = self.character.apply_influence(4, self.staff, "a favour called in")

        self.assertEqual(applied, 4)
        self.assertEqual(self.refresh().influence, 4)

    def test_influence_is_floored_at_zero(self):
        """A big enough loss stops at zero rather than going negative."""
        applied = self.character.apply_influence(-5, self.staff, "a costly mistake")

        self.assertEqual(self.refresh().influence, 0)
        self.assertEqual(applied, 0)

    def test_no_change_does_nothing(self):
        applied = self.character.apply_influence(0, self.staff, "nothing happened")

        self.assertEqual(applied, 0)

    def test_a_stale_instance_does_not_clobber_the_stored_value(self):
        """
        Two handles on the same character shouldn't lose each other's work:
        the delta has to be applied to what is stored, not to whatever this
        instance was holding when it was loaded.
        """
        self.character.apply_influence(6, self.staff, "an event")
        stale = type(self.character).objects.get(pk=self.character.pk)
        self.character.apply_influence(2, self.staff, "a favour")

        stale.apply_influence(3, self.staff, "another favour")

        self.assertEqual(self.refresh().influence, 11)

    def test_change_is_recorded_in_the_character_log(self):
        from django.contrib.admin.models import LogEntry

        self.character.apply_influence(4, self.staff, "a favour called in")

        entry = LogEntry.objects.filter(object_id=self.character.id).latest('action_time')
        self.assertIn("a favour called in", entry.change_message)
        self.assertIn("+4", entry.change_message)


class CorruptionLevelLookupTest(InfluenceTestCase):

    def test_lookup_takes_the_highest_threshold_reached(self):
        CorruptionLevel.objects.create(name="Tainted", threshold=10)
        middle = CorruptionLevel.objects.create(name="Marked", threshold=20)
        CorruptionLevel.objects.create(name="Lost", threshold=30)

        self.assertEqual(CorruptionLevel.for_influence(25), middle)

    def test_lookup_below_every_threshold_is_none(self):
        CorruptionLevel.objects.create(name="Tainted", threshold=10)

        self.assertIsNone(CorruptionLevel.for_influence(5))

    def test_lookup_with_no_ladder_configured_is_none(self):
        self.assertIsNone(CorruptionLevel.for_influence(100))

    def test_threshold_is_inclusive(self):
        tainted = CorruptionLevel.objects.create(name="Tainted", threshold=10)

        self.assertEqual(CorruptionLevel.for_influence(10), tainted)
