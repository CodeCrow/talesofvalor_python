"""
Tests for what happens when a player is marked as attended.

Creating an Attendance row is what "marked as attended" means; there is no
separate flag.  Doing it grants the attendance points and, the first time,
records where the player's game started.
"""
from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character
from talesofvalor.characters.tests.base import InfluenceTestCase


class AttendanceSaveTest(InfluenceTestCase):
    """The base set up gives us a player with an active character."""

    def player_cp(self):
        self.player.refresh_from_db()
        return self.player.cp_available

    def test_attending_grants_the_points(self):
        event = self.make_event("Spring 1")
        before = self.player_cp()

        Attendance.objects.create(player=self.player, event=event)

        self.assertEqual(
            self.player_cp(), before + Attendance.ATTENDANCE_CP)

    def test_points_are_granted_once_per_event(self):
        """
        Attendance has no unique constraint, so a duplicate row is possible.
        A duplicate is a mistake, not a second attendance to pay for.
        """
        event = self.make_event("Spring 1")
        before = self.player_cp()

        Attendance.objects.create(player=self.player, event=event)
        Attendance.objects.create(player=self.player, event=event)

        self.assertEqual(
            self.player_cp(), before + Attendance.ATTENDANCE_CP)

    def test_each_event_grants_its_own_points(self):
        first = self.make_event("Spring 1", days_out=-30)
        second = self.make_event("Spring 2", days_out=-10)
        before = self.player_cp()

        Attendance.objects.create(player=self.player, event=first)
        Attendance.objects.create(player=self.player, event=second)

        self.assertEqual(
            self.player_cp(), before + (2 * Attendance.ATTENDANCE_CP))

    def test_updating_attendance_does_not_grant_again(self):
        event = self.make_event("Spring 1")
        attendance = Attendance.objects.create(player=self.player, event=event)
        after_create = self.player_cp()

        attendance.save()

        self.assertEqual(self.player_cp(), after_create)

    def test_the_active_character_is_filled_in(self):
        """An attendance saved without a character picks up the active one."""
        event = self.make_event("Spring 1")

        attendance = Attendance.objects.create(player=self.player, event=event)

        self.assertEqual(attendance.character, self.character)

    def test_an_explicit_character_is_kept(self):
        event = self.make_event("Spring 1")
        other = Character.objects.create(
            player=self.player,
            name="Brenna"
        )

        attendance = Attendance.objects.create(
            player=self.player,
            event=event,
            character=other
        )

        self.assertEqual(attendance.character, other)

    def test_no_active_character_is_not_an_error(self):
        """A player with nobody active can still be marked as attended."""
        self.character.active_flag = False
        self.character.save(update_fields=['active_flag'])
        event = self.make_event("Spring 1")

        attendance = Attendance.objects.create(player=self.player, event=event)

        self.assertIsNone(attendance.character)

    def test_the_player_instance_is_usable_after_saving(self):
        """
        The points are added with an F() expression, which stays on the
        instance until it is read back.
        """
        event = self.make_event("Spring 1")

        attendance = Attendance.objects.create(player=self.player, event=event)

        self.assertIsInstance(attendance.player.cp_available, int)


class AttendanceDeleteTest(InfluenceTestCase):

    def player_cp(self):
        self.player.refresh_from_db()
        return self.player.cp_available

    def test_deleting_takes_the_points_back(self):
        event = self.make_event("Spring 1")
        before = self.player_cp()
        attendance = Attendance.objects.create(player=self.player, event=event)

        attendance.delete()

        self.assertEqual(self.player_cp(), before)

    def test_deleting_a_duplicate_does_not_take_points_back(self):
        """Only one of the two rows was ever paid for."""
        event = self.make_event("Spring 1")
        before = self.player_cp()
        Attendance.objects.create(player=self.player, event=event)
        duplicate = Attendance.objects.create(player=self.player, event=event)

        duplicate.delete()

        self.assertEqual(
            self.player_cp(), before + Attendance.ATTENDANCE_CP)

    def test_points_never_go_negative(self):
        """A player whose points were spent or reset can still be corrected."""
        event = self.make_event("Spring 1")
        attendance = Attendance.objects.create(player=self.player, event=event)
        self.player.cp_available = 1
        self.player.save(update_fields=['cp_available'])

        attendance.delete()

        self.assertEqual(self.player_cp(), 0)

    def test_deleting_the_only_event_clears_game_started(self):
        event = self.make_event("Spring 1")
        attendance = Attendance.objects.create(player=self.player, event=event)

        attendance.delete()

        self.player.refresh_from_db()
        self.assertIsNone(self.player.game_started)

    def test_deleting_the_first_event_moves_game_started_along(self):
        first = self.make_event("Spring 1", days_out=-30)
        second = self.make_event("Spring 2", days_out=-10)
        attendance = Attendance.objects.create(player=self.player, event=first)
        Attendance.objects.create(player=self.player, event=second)

        attendance.delete()

        self.player.refresh_from_db()
        self.assertEqual(self.player.game_started, second)

    def test_deleting_a_later_event_leaves_game_started_alone(self):
        first = self.make_event("Spring 1", days_out=-30)
        second = self.make_event("Spring 2", days_out=-10)
        Attendance.objects.create(player=self.player, event=first)
        attendance = Attendance.objects.create(player=self.player, event=second)

        attendance.delete()

        self.player.refresh_from_db()
        self.assertEqual(self.player.game_started, first)

    def test_a_staff_correction_survives_deletion(self):
        first = self.make_event("Spring 1", days_out=-30)
        corrected = self.make_event("Winter 0", days_out=-90)
        attendance = Attendance.objects.create(player=self.player, event=first)
        self.player.game_started = corrected
        self.player.save(update_fields=['game_started'])

        attendance.delete()

        self.player.refresh_from_db()
        self.assertEqual(self.player.game_started, corrected)

    def test_attending_and_deleting_leaves_no_trace(self):
        """The round trip is what makes a mistaken entry safe to undo."""
        event = self.make_event("Spring 1")
        before_cp = self.player_cp()

        attendance = Attendance.objects.create(player=self.player, event=event)
        attendance.delete()

        self.player.refresh_from_db()
        self.assertEqual(self.player.cp_available, before_cp)
        self.assertIsNone(self.player.game_started)


class GameStartedTest(InfluenceTestCase):

    def test_the_first_event_sets_game_started(self):
        event = self.make_event("Spring 1")
        self.assertIsNone(self.player.game_started)

        Attendance.objects.create(player=self.player, event=event)

        self.player.refresh_from_db()
        self.assertEqual(self.player.game_started, event)

    def test_a_later_event_does_not_move_game_started(self):
        first = self.make_event("Spring 1", days_out=-30)
        second = self.make_event("Spring 2", days_out=-10)

        Attendance.objects.create(player=self.player, event=first)
        Attendance.objects.create(player=self.player, event=second)

        self.player.refresh_from_db()
        self.assertEqual(self.player.game_started, first)

    def test_a_staff_correction_is_not_overwritten(self):
        """Staff fix game_started on the player form; attendance leaves it."""
        first = self.make_event("Spring 1", days_out=-30)
        corrected = self.make_event("Winter 0", days_out=-90)
        Attendance.objects.create(player=self.player, event=first)

        self.player.game_started = corrected
        self.player.save(update_fields=['game_started'])

        second = self.make_event("Spring 2", days_out=-10)
        Attendance.objects.create(player=self.player, event=second)

        self.player.refresh_from_db()
        self.assertEqual(self.player.game_started, corrected)
