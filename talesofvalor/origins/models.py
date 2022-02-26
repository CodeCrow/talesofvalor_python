"""
Origins (Attributes) of characters.

Describes character traits that are not learned or used in game.

These would be things like "peple", "nationality", "caste".

This should not be something that can be changed or learned.

These attributes may have an affect on the cost of abilities or grant
abilities or headers.
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField

class Origin(models.Model):
    """
    Backgrounds and Races and such.

    This will describe the attributes of a character.
    """

    PEOPLE = 'people'
    TRADITION = 'tradition'
    ORIGIN_TYPES = (
        (PEOPLE, 'People'),
        (TRADITION, 'Tradition'),
    )
    name = models.CharField(_("Name"), blank=False, max_length=100)
    description = HTMLField(blank=False)
    type = models.CharField(
        _("Type"),
        default=PEOPLE,
        choices=ORIGIN_TYPES,
        max_length=15
    )
    hidden_flag = models.BooleanField(_("Hidden?"), default=False)
    rules = GenericRelation('rules.Rule')

    created = models.DateTimeField(
        'date published',
        auto_now_add=True,
        editable=False
    )
    modified = models.DateTimeField(
        'last updated',
        auto_now=True,
        editable=False
    )
    created_by = models.ForeignKey(
        User,
        editable=False,
        related_name='%(app_label)s_%(class)s_author',
        null=True,
        on_delete=models.SET_NULL
    )
    modified_by = models.ForeignKey(
        User,
        editable=False,
        related_name='%(app_label)s_%(class)s_updater',
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name
