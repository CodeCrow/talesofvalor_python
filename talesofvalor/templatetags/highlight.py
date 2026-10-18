"""
Mark the terms a search matched inside the text it matched them in.

Kept generic on purpose: any list filtered by a text search can use this to
show the reader why a row came back.
"""
import re

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from talesofvalor import normalize_query


register = template.Library()

# Splits a fragment of HTML into tags and the text between them.  The
# capturing group keeps the tags in the result so the string can be put back
# together unchanged.
TAG_RE = re.compile(r'(<[^>]*>)')

# An HTML entity is a single character as far as the reader is concerned, so
# a term must not be marked inside one: highlighting the "amp" of "&amp;"
# would break it on the page.
ENTITY_RE = re.compile(r'(&[#\w]+;)')


def _mark_terms(text, pattern):
    """Wrap each match in a span, leaving entities alone."""
    pieces = []
    for piece in ENTITY_RE.split(text):
        if ENTITY_RE.fullmatch(piece):
            pieces.append(piece)
            continue
        pieces.append(
            pattern.sub(r'<span class="highlight">\g<0></span>', piece))
    return ''.join(pieces)


@register.filter(needs_autoescape=True)
def highlight(value, search_text, autoescape=True):
    """
    Mark every search term found in 'value'.

    usage: {{ bga.question|highlight:search_text }}

    'value' may be HTML, as the between game ability question and answer
    are, so the terms are only marked in the text between tags: marking
    inside a tag would corrupt it, and a term like "span" or "href" would
    otherwise rewrite the markup.

    The terms come from 'normalize_query', the same splitter 'get_query'
    uses to build the search, so what gets marked is what actually matched
    -- quoted phrases included.
    """
    if value is None:
        return ''
    if not search_text or not str(search_text).strip():
        return value

    # a value that is not already trusted HTML has to be escaped first,
    # exactly as '{{ value }}' would have done on its own.
    text = str(value)
    if autoescape:
        text = conditional_escape(value)

    terms = [term for term in normalize_query(str(search_text)) if term]
    if not terms:
        return value
    # One alternation rather than a pass per term, so a stretch of text is
    # marked once.  Marking term by term would re-scan the spans already
    # inserted and nest them.  Longest first: alternation takes the first
    # branch that matches, so "healing potion" wins over "healing".
    pattern = re.compile(
        '|'.join(
            re.escape(term)
            for term in sorted(terms, key=len, reverse=True)
        ),
        re.IGNORECASE
    )

    pieces = []
    for index, piece in enumerate(TAG_RE.split(text)):
        # odd pieces are the tags themselves and are left untouched.
        pieces.append(piece if index % 2 else _mark_terms(piece, pattern))
    return mark_safe(''.join(pieces))
