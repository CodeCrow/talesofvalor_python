import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from talesofvalor.attendance.models import Attendance
from talesofvalor.characters import models
from talesofvalor.events.models import Event
from talesofvalor.players.models import PEL


def character_settings(request):
    return {
        'POINT_CAP': models.POINT_CAP,
    }


def pel_deadline(request):
    """
    When the player's outstanding PEL is due, for the countdown in the header.

    Returns nothing at all unless there is something to count down to, which
    means all of:

    - an event that has finished and whose PEL deadline has not passed
    - a logged in player who attended it
    - at least one character of theirs who has not submitted a PEL for it

    The deadline itself is a date, so the moment counted to is the end of
    that day: a PEL due on the 14th can be sent any time during the 14th,
    which is the same rule the on time bonus uses.
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}
    try:
        player = user.player
    except ObjectDoesNotExist:
        # a signal gives every user a player, so this is belt and braces.
        return {}

    today = timezone.localdate()
    # the event whose PEL window is open: over, but not yet overdue.
    event = Event.objects.filter(
        event_date__lt=today,
        pel_due_date__gte=today
    ).order_by('-event_date').first()
    if not event:
        return {}

    attended = set(
        Attendance.objects
        .filter(player=player, event=event)
        .values_list('character', flat=True)
    )
    if not attended:
        return {}
    sent = set(
        PEL.objects
        .filter(event=event, character__in=attended, submitted__isnull=False)
        .values_list('character', flat=True)
    )
    if not attended - sent:
        # every character they played has had its PEL sent in.
        return {}

    # end of the due day, in the project's timezone.
    due = timezone.make_aware(
        datetime.datetime.combine(
            event.pel_due_date,
            datetime.time(23, 59, 59)
        )
    )
    return {
        'pel_deadline': due,
        'pel_deadline_event': event,
    }
