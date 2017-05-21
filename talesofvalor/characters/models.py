"""
Describes the character models.

These models describe a character and its relationship
to players.
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from filer.fields.image import FilerImageField

from talesofvalor.players.models import Player

class Character(models.Model):
    ALIVE = 'alive'
    DEAD = 'dead'
    STATUS_CHOICES = (
        (ALIVE, 'Alive'),
        (DEAD, 'Dead')
    )

    player = models.ForeignKey(Player)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='alive'
    )
    name = models.CharField(_("Character Name"), max_length=255)
    description = models.TextField(blank=True)
    history = models.TextField(blank=True)
    picture = FilerImageField(blank=True, null=True)
    player_notes = models.TextField(blank=True)
    staff_notes_visible = models.TextField(blank=True)
    staff_notes_hidden = models.TextField(blank=True)
    staff_attention_flag = models.BooleanField(default=False)
    npc_flag = models.BooleanField(default=False)
    active_flag = models.BooleanField(default=False)
    cp_spent = models.PositiveIntegerField(default=0)
    cp_available = models.PositiveIntegerField(default=0)
    cp_transferred = models.PositiveIntegerField(default=0)

    created = models.DateTimeField('date published', auto_now_add=True, editable=False)
    modified = models.DateTimeField('last updated', auto_now=True, editable=False)
    created_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_author', null=True)
    modified_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_updater', null=True)
