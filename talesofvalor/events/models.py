"""
Describes the game events.

These models describe the game events.
"""
from datetime import date

from django.contrib.auth.models import User
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


    def get_absolute_url(self):
        """
        Return the absolute URL.

        This is the canonical URL to show the detail page
        for an Event.
        """
        return reverse('events:event_detail', kwargs={'pk': self.pk})
