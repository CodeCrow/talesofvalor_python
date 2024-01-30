"""
Describes the game events.

These models describe the game events.
"""
from datetime import date, timedelta

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField


EVENT_MEALPLAN_PRICE = 35


class Event(models.Model):
    name = models.CharField(
        help_text=_("For reference, such as \"Spring 2, 2010\""),
        max_length=255
    )
    event_date = models.DateField()
    pel_due_date = models.DateField()
    bgs_due_date = models.DateField()
    oog_p = models.BooleanField(_("Out of game event"), default=False)
    bgs_p = models.BooleanField(_("Allow Between Game Skills"), default=True)
    notes = HTMLField(blank=True, default='')
    summary = HTMLField(blank=True, default='')

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return "{} - {}".format(
            self.name,
            self.event_date.strftime("%m-%d-%Y")
        )

    @classmethod
    def previous_event(cls):
        event_range_beginning = date.today() - timedelta(days=3)
        try:
            return cls.objects.filter(event_date__lt=event_range_beginning)\
                .order_by('-event_date').first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def next_event(cls):
        '''
        When looking for the next event, make sure we are not in a 
        current event.
        '''
        event_range_end = date.today() - timedelta(days=3)
        try:
            return cls.objects.filter(event_date__gt=event_range_end)\
                .order_by('event_date').first()
        except cls.DoesNotExist:
            return None

    @property
    def previous(self):
        try:
            return type(self).objects.filter(event_date__lt=self.event_date)\
                .order_by('-event_date').first()
        except self.DoesNotExist:
            return None

    @property
    def next(self):
        try:
            return type(self).objects.filter(event_date__gt=self.event_date)\
                .order_by('-event_date').first()
        except self.DoesNotExist:
            return None

    def attended(self, character):
        return self.attendance_set.filter(player=character.player).exists()

    def attended_player(self, player):
        return self.attendance_set.filter(player=player).exists()

    def get_absolute_url(self):
        """
        Return the absolute URL.

        This is the canonical URL to show the detail page
        for an Event.
        """
        return reverse('events:event_detail', kwargs={'pk': self.pk})


class EventRegistrationItem(models.Model):
    """
    A structure that binds up the different ways that an event could be
    registered for.

    For example, and Item might have a season's worth of events.  Or a Years.
    """
    name = models.CharField(
        help_text=_("For reference, such as \"Season Pass\""),
        max_length=255
    )
    order = models.IntegerField(
        help_text=_("What order should this appear on the page?"),
        default=0
    )
    events = models.ManyToManyField(Event, related_name="events")
    available = models.BooleanField(
        help_text=_("Is this still available?"),
        default=True
    )
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def get_absolute_url(self):
        """
        Return the absolute URL.

        This is the canonical URL to show the detail page
        for an EventRegistrationItem.
        """
        return reverse('events:eventregistrationitem_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return "{}".format(
            self.name
        )

    class Meta:
        ordering = ['order']
