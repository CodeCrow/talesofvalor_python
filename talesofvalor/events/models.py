"""
Describes the game events.

These models describe the game events.
"""
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField

from talesofvalor.characters.models import Character


class Event(models.Model):
    name = models.CharField(max_length=255)
    event_date = models.DateField(default=date.today)
    pel_due_date = models.DateField(default=date.today)
    bgs_due_date = models.DateField(default=date.today)
    oog_p = models.BooleanField(_("Out of game event"), default=False)  
    bgs_p = models.BooleanField(_("Allow Between Game Skills"), default=True)
    notes = HTMLField(blank=True, default='')
    summary = HTMLField(blank=True, default='')

class Messages(models.Model):
    event = models.ForeignKey(Event)
    character = models.ForeignKey(Character)
    message = HTMLField(blank=True, default='')

    created = models.DateTimeField('date published', auto_now_add=True, editable=False)
    modified = models.DateTimeField('last updated', auto_now=True, editable=False)
    created_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_author', null=True)
    modified_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_updater', null=True)
