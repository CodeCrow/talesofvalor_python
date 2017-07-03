"""
Describes the game events.

These models describe the game events.
"""
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField


class Event(models.Model):
    name = models.CharField(max_length=255)
    event_date = models.DateField(default=date.today)
    pel_due_date = models.DateField(default=date.today)
    bgs_due_date = models.DateField(default=date.today)
    oog_p = models.BooleanField(_("Out of game event"), default=False)  
    bgs_p = models.BooleanField(_("Allow Between Game Skills"), default=True)
    notes = HTMLField(blank=True, default='')
    summary = HTMLField(blank=True, default='')
