"""
Describes the between game abilities.

Between game abilities are associate with the characters who are using
them and are assigned to staff members.  Staff members supply answers and
can add comments for discussion about the player request.

Each request also is associated with the event that it is the "ask" for.

Each request also as a "count" of the skill type that is making the request.
This is the "power" of each request.
"""
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from djangocms_text_ckeditor.fields import HTMLField

from taggit.managers import TaggableManager

from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character
from talesofvalor.players.models import Player, limit_to_staff
from talesofvalor.skills.models import HeaderSkill
from talesofvalor.events.models import Event


class BetweenGameAbility(models.Model):
    """
    Between Game Abilities.

    Holds the question and the links to the other parts of the game.
    """

    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ability = models.ForeignKey(
        HeaderSkill,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    non_ability_source_flag = models.BooleanField(
        _("Other"),
        help_text=_("Choose this for abilities granted by potions or other, non-ability sources."),
        default=False
    )
    count = models.PositiveIntegerField(
        help_text=_("If you enter 0, please include a description of where you are getting the ability from.")
    )
    question = HTMLField(blank=False)
    answer = HTMLField(blank=True)
    assigned_to = models.ForeignKey(
        Player,
        null=True,
        limit_choices_to=limit_to_staff,
        on_delete=models.SET_NULL
    )
    answer_date = models.DateTimeField(
        _('answered'),
        editable=False,
        null=True
    )
    # taggit tags
    tags = TaggableManager(blank=True)
    created = models.DateTimeField(
        _('submitted'),
        auto_now_add=True, editable=False)
    modified = models.DateTimeField(_('last updated'), auto_now=True, editable=False)
    created_by = models.ForeignKey(Player, editable=False, related_name='%(app_label)s_%(class)s_author', null=True, on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(Player, editable=False, related_name='%(app_label)s_%(class)s_updater', null=True, on_delete=models.SET_NULL)

    @classmethod
    def limit_assigned_to(cls):
        return {"pub_date__lte": datetime.date.today()}

    def answer_available(self):
        """
        an available answer is one whose relavent event is in the past 
        and the player has attended an event since.
        """
        return Attendance.objects.filter(
            player=self.character.player
        ).filter(
            event__event_date__gte=self.event.next.event_date
        ).exists()

    def get_absolute_url(self):
        """
        Get to the specific display for an instance.
        """
        return reverse('betweengameabilities:betweengameability_detail', kwargs={'pk': self.pk})


    def __str__(self):
        return f"{self.character} -> {self.event}"

    class Meta:
        verbose_name = "Between Game Ability"
        verbose_name_plural = "Between Game Abilities"
