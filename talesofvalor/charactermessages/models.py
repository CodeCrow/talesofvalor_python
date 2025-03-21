"""
Messages for characters at events.

Contains information that should be passed on to a
character at a particular event.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField

from talesofvalor.characters.models import Character
from talesofvalor.events.models import Event

class CharacterMessage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    message = HTMLField(blank=True, default='')

    created = models.DateTimeField(_('date published'), auto_now_add=True, editable=False)
    modified = models.DateTimeField(_('last updated'), auto_now=True, editable=False)
    created_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_author', null=True, on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_updater', null=True, on_delete=models.SET_NULL)