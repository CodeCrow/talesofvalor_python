"""
Skills and abilities that characters can use.

Characters have different things that they can do.

These skills have a cost to the character.

The costs can be changed or removed throught certain rules.

Skills may also come under "Headers" that must be purchased before
they can purchase the skills that belong to that header.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField


class Skill(models.Model):
    """
    Skill representing things that characters can do.

    Attached to headers that are attached to characters.
    """
    name = models.CharField(max_length=100)
    tag = models.CharField(max_length=100, blank=True, default='')
    description = HTMLField(blank=False)
    single_flag = models.BooleanField(
        _("Single Purchase?"),
        help_text=_("""
            Indicates that you only have to buy it once
            (like for weapon skills)
            """),
        default=False
    )
    bgs_flag = models.BooleanField(default=False)
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

    class Meta:
        ordering = ['tag', 'name']

    def __str__(self):
        return self.name

    @property
    def headers(self):
        return ', '.join([i for i in self.headerskill_set.values_list(
            "header__name",
            flat=True
        )])


class Header(models.Model):
    """
    Header containing skills.

    Object that skills are attached to.  Every skill belongs to a header
    of some sort.

    Skills can be part of multiple headers with different costs
    under each.
    """

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True, default='')
    description = HTMLField(blank=False)
    cost = models.PositiveIntegerField(null=False, blank=False)
    hidden_flag = models.BooleanField("hidden?", default=False)
    skills = models.ManyToManyField(Skill, through='HeaderSkill')
    created = models.DateTimeField('date published', auto_now_add=True, editable=False)
    modified = models.DateTimeField('last updated', auto_now=True, editable=False)
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

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class HeaderSkill(models.Model):
    """
    Links up the Header and skills.

    This also holds the cost for a skill under a specific header,
    because skills cost different amounts under different headers.
    """

    header = models.ForeignKey(Header, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    cost = models.PositiveIntegerField(null=False, blank=False)
    dabble_flag = models.BooleanField(default=False)
    capstone_flag = models.BooleanField(
        _("Is this a capstone?"),
        help_text=_("""
            Indicates that this is a capstone granted when
            requirements are met.
            (like for weapon skills)
            """),
        default=False)

    def __str__(self):
        return "{header}:{skill}[{cost}]".format(
            header=self.header,
            skill=self.skill,
            cost=self.cost
        )
