"""
Tests for the 'highlight' filter.

The between game ability question and answer are HTMLField, so the value
reaching the filter is real markup that renders unescaped.  Marking terms in
it has to leave the tags alone.
"""
from django.test import TestCase
from django.utils.safestring import SafeString, mark_safe

from talesofvalor.templatetags.highlight import highlight


MARK = '<span class="highlight">{}</span>'


class HighlightFilterTest(TestCase):

    def test_marks_a_plain_word(self):
        self.assertEqual(
            highlight(mark_safe("a healing potion"), "healing"),
            "a {} potion".format(MARK.format("healing"))
        )

    def test_marking_is_case_insensitive_but_keeps_the_original_case(self):
        """The reader should see their text as written, not as searched."""
        self.assertEqual(
            highlight(mark_safe("A Healing potion"), "healing"),
            "A {} potion".format(MARK.format("Healing"))
        )

    def test_every_occurrence_is_marked(self):
        result = highlight(mark_safe("potion of potions"), "potion")

        self.assertEqual(result.count('class="highlight"'), 2)

    def test_terms_inside_tags_are_left_alone(self):
        """
        Searching for a word that also appears in the markup must not
        rewrite the markup.  'span' is the dangerous case.
        """
        result = highlight(
            mark_safe('<span class="x">a span of time</span>'), "span")

        self.assertEqual(
            result,
            '<span class="x">a {} of time</span>'.format(MARK.format("span"))
        )

    def test_attributes_are_not_touched(self):
        result = highlight(
            mark_safe('<a href="/potion/">buy a potion</a>'), "potion")

        self.assertEqual(
            result,
            '<a href="/potion/">buy a {}</a>'.format(MARK.format("potion"))
        )

    def test_entities_are_not_broken(self):
        """Marking the 'amp' inside '&amp;' would corrupt it."""
        result = highlight(mark_safe("salt &amp; marshwort"), "amp")

        self.assertEqual(result, "salt &amp; marshwort")

    def test_a_quoted_phrase_is_marked_as_one_run(self):
        result = highlight(mark_safe("a healing potion"), '"healing potion"')

        self.assertEqual(
            result, "a {}".format(MARK.format("healing potion")))

    def test_several_words_are_each_marked(self):
        result = highlight(mark_safe("a healing potion"), "healing potion")

        self.assertEqual(
            result,
            "a {} {}".format(
                MARK.format("healing"), MARK.format("potion"))
        )

    def test_the_longest_term_wins_where_they_overlap(self):
        """
        'healing' and 'healing potion' both match at the same spot; marking
        the short one first would leave the long one unmatchable.
        """
        result = highlight(
            mark_safe("a healing potion"), '"healing potion" healing')

        self.assertEqual(
            result, "a {}".format(MARK.format("healing potion")))

    def test_an_empty_search_changes_nothing(self):
        original = mark_safe("<p>a healing potion</p>")

        self.assertEqual(highlight(original, ""), original)
        self.assertEqual(highlight(original, "   "), original)
        self.assertEqual(highlight(original, None), original)

    def test_no_match_changes_nothing(self):
        original = mark_safe("<p>a healing potion</p>")

        self.assertEqual(highlight(original, "basilisk"), original)

    def test_a_regex_in_the_search_is_treated_literally(self):
        """A search is plain text, so '.*' must not match everything."""
        result = highlight(mark_safe("a healing potion"), ".*")

        self.assertEqual(result, "a healing potion")

    def test_unsafe_input_is_still_escaped(self):
        """
        A value that is not already trusted HTML has to be escaped, exactly
        as '{{ value }}' would have escaped it on its own.
        """
        result = highlight("<script>alert(1)</script> potion", "potion")

        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)
        self.assertIn(MARK.format("potion"), result)

    def test_the_result_is_safe_to_render(self):
        result = highlight(mark_safe("a healing potion"), "healing")

        self.assertIsInstance(result, SafeString)

    def test_none_renders_as_nothing(self):
        self.assertEqual(highlight(None, "healing"), '')
