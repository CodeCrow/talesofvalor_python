"""
Describes the between game skills.

Between game skills are associate with the characters who are using
them and are assigned to staff members.  Staff members supply answers and
can add comments for discussion about the player request.

Each request also is associated with the even that it is the "ask" for.

Each request also as a "count" of the skill type that is making the request.
This is the "power" of each request.
"""
from django.db import models
from django.utils.translation import ugettext as _

from djangocms_text_ckeditor.fields import HTMLField

from talesofvalor.characters.models import Character
from talesofvalor.players.models import Player
from talesofvalor.skills.models import Skill
from talesofvalor.events.models import Event


class BetweenGameSkill(models.Model):
    """
    Between Game Skills.

    Holds the question and the links to the other parts of the game.
    """

    character = models.ForeignKey(Character)
    event = models.ForeignKey(Event)
    skill = models.ForeignKey(Skill)
    count = models.PositiveIntegerField()
    question = HTMLField(blank=False)
    answer = HTMLField(blank=True)
    assigned_to = models.ForeignKey(
        Player,
        null=True,
        limit_choices_to={'is_staff': True}
    )
    submit_date = models.DateTimeField(
        _('submitted'),
        auto_now=True,
        editable=False
    )
    answer_date = models.DateTimeField(
        _('answered'),
        editable=False
    )
