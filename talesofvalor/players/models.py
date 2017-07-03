"""
Describes the player models.

These models describe the player and its relationship to the
django authentication user models.
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from djangocms_text_ckeditor.fields import HTMLField

from talesofvalor.events.models import Event


class Player(models.Model):
    """
    Player of a game.

    An individual who is playing a game.  All users are players
    of some sort.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game_started = models.ForeignKey(Event, null=True)
    cp_available = models.PositiveIntegerField(default=0)

class PEL(models.Model):
    """
    (P)ost (E)vent (L)etter.

    Letter and information describing a player's experience at an event.
    """
    RATINGS_CHOICES = (
        (5, 'Amazing'),
        (4, 'Good'),
        (3, 'Average'),
        (2, 'Fair'),
        (1, 'Poor'),
    )

    player = models.ForeignKey(Player)
    event = models.ForeignKey(Event)
    created = models.DateTimeField(
        _('date created'),
        null=True,
        auto_now_add=True,
        editable=False
    )
    modified = models.DateTimeField(
        _('last updated'),
        null=True,
        auto_now=True,
        editable=False
    )
    likes = models.TextField(blank=True, default='')
    dislikes = models.TextField(blank=True, default='')
    best_moments = models.TextField(blank=True, default='')
    worst_moments = models.TextField(blank=True, default='')
    learned = models.TextField(blank=True, default='')
    data = HTMLField(blank=True, default='')
    rating = models.PositiveIntegerField(choices=RATINGS_CHOICES)
