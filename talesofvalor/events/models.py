"""
Describes the game events.

These models describe the game events.
"""
from datetime import date

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField


class Event(models.Model):
    name = models.CharField(
        help_text=_("For reference, such as \"Spring 2, 2010\""),
        max_length=255
    )
    event_date = models.DateField(default=date.today)
    pel_due_date = models.DateField(default=date.today)
    bgs_due_date = models.DateField(default=date.today)
    oog_p = models.BooleanField(_("Out of game event"), default=False)
    bgs_p = models.BooleanField(_("Allow Between Game Skills"), default=True)
    notes = HTMLField(blank=True, default='')
    summary = HTMLField(blank=True, default='')

    def __str__(self):
        return "{} - {}".format(
                self.name,
                self.event_date.strftime("%m-%d-%Y")
            )

    @classmethod
    def previous_event(cls):
        try:
            return cls.objects.filter(event_date__lt=date.today())\
                .order_by('-event_date').first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def next_event(cls):
        try:
            return cls.objects.filter(event_date__gt=date.today())\
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

    def get_absolute_url(self):
        """
        Return the absolute URL.

        This is the canonical URL to show the detail page
        for an Event.
        """
        return reverse('events:event_detail', kwargs={'pk': self.pk})
