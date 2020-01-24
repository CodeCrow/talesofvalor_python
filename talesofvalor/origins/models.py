"""
Origins (Attributes) of characters.

Describes character traits that are not learned or used in game.

These would be things like "race", "nationality", "caste".

This should not be something that can be changed or learned.

These attributes may have an affect on the cost of abilities or grant
abilities or headers.
"""
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField

from talesofvalor.skills.models import Skill


class Origin(models.Model):
    """
    Backgrounds and Races and such.

    This will describe the attributes of a character.
    """

    RACE = 'race'
    BACKGROUND = 'background'
    ORIGIN_TYPES = (
        (RACE, 'Race'),
        (BACKGROUND, 'Background'),
    )
    name = models.CharField(_("Name"), blank=False, max_length=100)
    description = HTMLField(blank=False)
    type = models.CharField(
        _("Type"),
        default=RACE,
        choices=ORIGIN_TYPES,
        max_length=15
    )
    hidden_flag = models.BooleanField(_("Hidden?"), default=False)
    skills = models.ManyToManyField(Skill, through='OriginSkill')

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


class OriginSkill(models.Model):
    """
    Links up skills and Origins.

    Because some origins give characters abilities, this will automatically
    give those characters the skills that they should have.
    """

    origin = models.ForeignKey(Origin, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(null=False, default=1)
