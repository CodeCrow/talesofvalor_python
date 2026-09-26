"""
Rolling influence forward for an event.

Staff record each character's end of game total in
``CharacterEventInfluence.influence_input`` after a game.  Processing the
event then rolls everyone forward, and can be reversed if something was
entered wrong.

The per character change itself is ``Character.apply_influence``.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from talesofvalor.characters.models import (
    INFLUENCE_REGENERATION,
    CharacterEventInfluence,
    CorruptionLevel,
)


def has_later_processing(event):
    """
    Has any event after this one already had its influence processed?

    Influence rolls forward from one event to the next, so processing has to
    happen in date order.  Processing or reversing this event after a later
    one would leave every event after it holding a start value that no longer
    follows from anything.
    """
    return CharacterEventInfluence.objects.filter(
        event__event_date__gt=event.event_date,
        processed_at__isnull=False
    ).exists()


def _assert_no_later_processing(event):
    """Refuse to touch an event if a later one has already been processed."""
    if has_later_processing(event):
        raise ValidationError(
            "A later event has already been processed.  Reverse that event "
            "before changing this one, so influence rolls forward in order."
        )


def ensure_event_rows(event):
    """
    Make sure every attendee has an influence row for this event.

    Safe to call repeatedly; the unique constraint on (event, character)
    means re-running just finds the existing rows.
    """
    with transaction.atomic():
        for character in event.attendees_character:
            CharacterEventInfluence.objects.get_or_create(
                event=event,
                character=character
            )
    return CharacterEventInfluence.objects\
        .filter(event=event)\
        .select_related('character', 'character__player__user', 'corruption_level')


def process_event_influence(event, user):
    """
    Roll influence forward for everyone at an event.

    For each character with an influence input:

    1) Start of Game Influence takes the character's current influence
    2) End of Game Influence takes the Influence Input
    3) the regeneration amount comes off End of Game Influence
    4) if Start is less than End, the character is flagged for a Corruption
    5) a flagged character's corruption level is resolved from End

    Rows without an input are left alone, so staff can process a partially
    entered event and come back to the rest.  Already processed rows are
    skipped, which makes running this twice harmless.
    """
    _assert_no_later_processing(event)
    counts = {'processed': 0, 'flagged': 0, 'skipped': 0}
    with transaction.atomic():
        rows = CharacterEventInfluence.objects\
            .select_for_update()\
            .filter(event=event, processed_at__isnull=True)\
            .select_related('character')
        now = timezone.now()
        for row in rows:
            if row.influence_input is None:
                counts['skipped'] += 1
                continue
            character = row.character
            row.start_influence = character.influence
            row.end_influence = max(
                0,
                row.influence_input - INFLUENCE_REGENERATION
            )
            row.corruption_flag = row.start_influence < row.end_influence
            row.corruption_level = CorruptionLevel.for_influence(
                row.end_influence
            ) if row.corruption_flag else None
            row.processed_at = now
            row.processed_by = user
            row.save(update_fields=[
                'start_influence',
                'end_influence',
                'corruption_flag',
                'corruption_level',
                'processed_at',
                'processed_by',
            ])
            character.apply_influence(
                row.delta,
                user,
                f"{event} influence was processed"
            )
            counts['processed'] += 1
            if row.corruption_flag:
                counts['flagged'] += 1
    return counts


def unprocess_event_influence(event, user):
    """
    Undo the roll forward for an event.

    Applies the opposite of the change each row made rather than writing the
    old value back, so a manual adjustment made after processing survives
    being reversed.  The influence inputs are kept, so staff can correct a
    typo and process again.
    """
    _assert_no_later_processing(event)
    counts = {'reversed': 0}
    with transaction.atomic():
        rows = CharacterEventInfluence.objects\
            .select_for_update()\
            .filter(event=event, processed_at__isnull=False)\
            .select_related('character')
        for row in rows:
            row.character.apply_influence(
                -row.delta,
                user,
                f"{event} influence processing was reversed"
            )
            row.start_influence = None
            row.end_influence = None
            row.corruption_flag = False
            row.corruption_level = None
            row.processed_at = None
            row.processed_by = None
            row.save(update_fields=[
                'start_influence',
                'end_influence',
                'corruption_flag',
                'corruption_level',
                'processed_at',
                'processed_by',
            ])
            counts['reversed'] += 1
    return counts
