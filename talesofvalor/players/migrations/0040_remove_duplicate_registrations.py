"""
Remove duplicate registrations so a unique constraint can be added.

'RegistrationRequest.request_complete' used to be callable more than once for
the same request - two of its callers fire on a GET, so a reload or a prefetch
was enough - and each call created a fresh Registration per event.  The next
migration adds a unique constraint on (registration_request, event), which
can't be applied while those extra rows are still there.

Within each duplicated group one row is kept and the rest are deleted.  The
row to keep is chosen, in order of preference, by:

1. Hand-entered data.  'cabin' and 'notes' aren't copied from the request,
   they're filled in by staff afterwards, so a row carrying either outranks
   one that doesn't.  Never throw away somebody's typing.
2. Agreement with the parent request.  'request_complete' copies the travel,
   meal and payment fields straight off the RegistrationRequest, so the row
   matching the most of them is the one that reflects what the player
   actually asked for.
3. The lowest id, to make the outcome deterministic when rows are identical
   (which, in the data this was written against, 57 of 58 groups were).

This only looks at rows with a registration_request.  Registrations entered by
hand have none, and NULLs don't collide in a unique index.
"""
from django.db import migrations


# the fields 'request_complete' copies from the RegistrationRequest
COPIED_FROM_REQUEST = (
    'no_car_flag',
    'site_transportation',
    'vehicle_make',
    'vehicle_model',
    'vehicle_color',
    'vehicle_registration',
    'local_contact',
    'mealplan_flag',
    'food_allergies',
    'vegetarian_flag',
    'vegan_flag',
    'pay_at_door_flag',
    'already_paid_flag',
)


def keep_score(registration):
    """
    How strong a candidate this row is for being the one that survives.

    Higher wins.  Hand-entered text is weighted above field agreement so that
    a single staff note outranks any number of matching flags.
    """
    score = 0
    for field in ('cabin', 'notes'):
        if (getattr(registration, field) or '').strip():
            score += 100
    event_reg_request = registration.registration_request
    for field in COPIED_FROM_REQUEST:
        if getattr(registration, field) == getattr(event_reg_request, field):
            score += 1
    return score


def remove_duplicate_registrations(apps, schema_editor):
    from django.db.models import Count

    Registration = apps.get_model('players', 'Registration')

    duplicated = (
        Registration.objects
        .filter(registration_request__isnull=False)
        .values('registration_request', 'event')
        .annotate(row_count=Count('id'))
        .filter(row_count__gt=1)
    )

    doomed = []
    for group in duplicated:
        candidates = list(
            Registration.objects
            .filter(
                registration_request=group['registration_request'],
                event=group['event']
            )
            .select_related('registration_request')
            .order_by('id')
        )
        # 'order_by' above settles ties: 'max' keeps the first row it sees
        # with the winning score, which is the lowest id.
        keeper = max(candidates, key=keep_score)
        doomed.extend(
            candidate.pk for candidate in candidates
            if candidate.pk != keeper.pk
        )

    if doomed:
        Registration.objects.filter(pk__in=doomed).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0039_alter_pel_options_pel_tags_alter_pel_donations_props_and_more'),
    ]

    operations = [
        # deleted rows can't be brought back, so there is nothing to reverse.
        migrations.RunPython(
            remove_duplicate_registrations,
            migrations.RunPython.noop
        ),
    ]
