"""
Show the duplicate registrations that migration 0040 would remove.

Run this before deploying that migration, so the rows it deletes are on
paper first:

    ./manage.py show_duplicate_registrations --settings=talesofvalor.settings.production

The migration deletes rows; this only reads.  It reuses the migration's own
'keep_score' so the two can't drift apart and tell different stories.
"""
from django.core.management.base import BaseCommand
from django.db.models import Count

from talesofvalor.players.models import Registration


def _keep_score():
    """Borrow the migration's rule rather than restating it here."""
    from importlib import import_module
    module = import_module(
        'talesofvalor.players.migrations.0040_remove_duplicate_registrations'
    )
    return module.keep_score


class Command(BaseCommand):
    help = "List the duplicate registrations that migration 0040 removes."

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose-rows',
            action='store_true',
            help="Show every field that differs within a group."
        )

    def handle(self, *args, **options):
        keep_score = _keep_score()

        groups = (
            Registration.objects
            .filter(registration_request__isnull=False)
            .values('registration_request', 'event')
            .annotate(row_count=Count('id'))
            .filter(row_count__gt=1)
            .order_by('registration_request')
        )

        total_kept = total_removed = 0
        differing = []

        for group in groups:
            rows = list(
                Registration.objects
                .filter(
                    registration_request=group['registration_request'],
                    event=group['event']
                )
                .select_related(
                    'registration_request', 'event', 'player__user')
                .order_by('id')
            )
            keeper = max(rows, key=keep_score)
            doomed = [row for row in rows if row.pk != keeper.pk]
            total_kept += 1
            total_removed += len(doomed)

            # a group whose rows are identical needs no human attention; one
            # where they differ is a judgement the migration is making for us.
            comparable = ('cabin', 'notes', 'mealplan_flag', 'food_allergies',
                          'registration_type', 'pay_at_door_flag',
                          'already_paid_flag')
            same = all(
                all(getattr(row, f) == getattr(rows[0], f)
                    for f in comparable)
                for row in rows[1:]
            )
            if not same:
                differing.append((group, rows, keeper))

            self.stdout.write(
                "request {} / event {} ({})".format(
                    group['registration_request'],
                    group['event'],
                    keeper.event
                )
            )
            self.stdout.write(
                "    player  {}".format(keeper.player)
            )
            self.stdout.write(self.style.SUCCESS(
                "    keep    id={}".format(keeper.pk)
            ))
            for row in doomed:
                self.stdout.write(self.style.WARNING(
                    "    remove  id={}".format(row.pk)
                ))
            if options['verbose_rows'] and not same:
                for row in rows:
                    self.stdout.write("      id={} {}".format(
                        row.pk,
                        {f: getattr(row, f) for f in comparable}
                    ))

        self.stdout.write("")
        self.stdout.write("duplicate groups:   {}".format(total_kept))
        self.stdout.write("rows kept:          {}".format(total_kept))
        self.stdout.write("rows to be removed: {}".format(total_removed))
        self.stdout.write("registrations now:  {}".format(
            Registration.objects.count()))

        if differing:
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE(
                "{} group(s) hold rows that are NOT identical; the migration "
                "picks between them. Re-run with --verbose-rows to see the "
                "fields.".format(len(differing))
            ))
