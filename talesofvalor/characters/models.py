"""
Describes the character models.

These models describe a character and its relationship
to players.
"""
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext as _

from filer.fields.image import FilerImageField

from talesofvalor.players.models import Player
from talesofvalor.skills.models import Header, Skill
from talesofvalor.origins.models import Origin


class Character(models.Model):
    """
    Character a player can play.

    Players can have more than one character, but only one can be active at a
    time.
    Staff can have multiple characters who are active at the same time.
    """

    ALIVE = 'alive'
    DEAD = 'dead'
    RETIRED = 'retired'
    STATUS_CHOICES = (
        (ALIVE, 'Alive'),
        (DEAD, 'Dead'),
        (RETIRED, 'Retired'),
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
    # The headers and skills that a character has.
    headers = models.ManyToManyField(Header)
    skills = models.ManyToManyField(Skill, through='CharacterSkills')
    # origins.  Should only be as many as there are types.
    origins = models.ManyToManyField(Origin)

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
    created_by = models.ForeignKey(
        User,
        editable=False,
        related_name='%(app_label)s_%(class)s_author',
        null=True
    )
    modified_by = models.ForeignKey(
        User,
        editable=False,
        related_name='%(app_label)s_%(class)s_updater',
        null=True
    )

    def get_absolute_url(self):
        return reverse('characters:character_detail', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name

class CharacterSkills(models.Model):
    """
    Links chracters with their skills.

    Indicates what skills a character has and how many of them exist.
    """

    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(null=False, default=1)


class CharacterLog(models.Model):
    """
    Log of changes to character.

    Whenever anyone makes a change to a character, an entry to
    this log should be added so any problems or bad actions can be traced.
    """

    character = models.ForeignKey(Character)
    message = models.TextField(_("Log Message"))
    created = models.DateTimeField(
        _('date created'),
        auto_now_add=True,
        editable=False
    )
    created_by = models.ForeignKey(
        User,
        editable=False,
        related_name='%(app_label)s_%(class)s_author',
        null=True
    )

class CharacterGrant(models.Model):
    """
    Tracks special skills and headers granted to a character.

    Some origins or events trigger the granting of headers or skills.
    These do not count against spent character points.

    TODO: I feel like there is a way to do this without grants since the
    system will know what rules have been or should run.

    Grants would then turn into a "special" that could be granted by a
    staff member.
    """

    SKILL_GRANT = 'SkillGrant'
    HEADER_GRANT = 'HeaderGrant'
    TYPE_CHOICES = (
        (SKILL_GRANT, 'Skill Grant'),
        (HEADER_GRANT, 'Header Grant')
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='SkillGrant'
    )
    character = models.ForeignKey(Character)
    correlated_id = models.PositiveIntegerField()
    reason = models.TextField()
    free = models.BooleanField(default=False)
    picks_remaining = models.PositiveIntegerField(default=10000)

