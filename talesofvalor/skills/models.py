"""
Skills and abilities that characters can use.

Characters have different things that they can do.

These skills have a cost to the character.

The costs can be changed or removed throught certain rules.

Skills may also come under "Headers" that must be purchased before
they can purchase the skills that belong to that header.
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField


class Skill(models.Model):
    """
    Skill representing things that characters can do.

    Attached to headers that are attached to characters.
    """
    name = models.CharField(max_length=100)
    # done like the to prevent circular imports
    prerequisites = GenericRelation('rules.Prerequisite')
    prerequisite_groups = GenericRelation('rules.PrerequisiteGroup')
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
    bgs_flag = models.BooleanField(
        _("Between Game Ability"),
        help_text=_("""
            An ability that is typically used between events instead of during them.
            """),
        default=False
    )
    perk_flag = models.BooleanField(
        _("This is a Perk"),
        help_text=_("""
            A permanent ability that typically takes the form of a passive 
            benefit that permanently enhances a player’scapabilities.
            """),
        default=False
    )

    rules = GenericRelation('rules.Rule', related_query_name='rules')
    
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
        ordering = ['headerskill__cost', 'name']
        """Add permissions."""

        permissions = (
            ("view_all_skills", "View All Skills when choosing"),
        )

    def __str__(self):
        return self.name

    @property
    def headers(self):
        return ', '.join([i for i in self.headerskill_set.values_list(
            "header__name",
            flat=True
        )])

    @classmethod
    def skillhash(cls):
        """
        Create the base hash of skills and costs.
        {
            51: {'skills': {
                    248: {'cost': 3, 'purchased': 0}, 
                    49: {'cost': 3, 'purchased': 0},
                    250: {'cost': 3, 'purchased': 0},
                    251: {'cost': 3, 'purchased': 0},
                    252: {'cost': 3, 'purchased': 0}
                },
                'cost': 0}}
        }
        It will be updated by the character.
        """
        headers = Header.objects.all().order_by('-open_flag')
        skill_hash = {
            h.id: {
                'skills': {
                    s.skill_id: {
                        'name': s.skill.name,
                        'headerskill': s.id,
                        'cost': s.cost,
                        'purchased': 0
                    }
                    for s in h.headerskill_set.all()
                }
            }
            for h in headers
        }
        for h in headers:
            skill_hash[h.id]['cost'] = h.cost

        return skill_hash


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
    open_flag = models.BooleanField(
        "open?", 
        help_text=_("""
        Header is automatically 'open' without the need for purchase.
        """),
        default=False
    )
    skills = models.ManyToManyField(Skill, through='HeaderSkill')

    rules = GenericRelation('rules.Rule', related_query_name='rules')
    # done like this to prevent circular imports
    prerequisites = GenericRelation('rules.Prerequisite')
    prerequisite_groups = GenericRelation('rules.PrerequisiteGroup')
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
    magic_flag = models.BooleanField(
        _("Is this magical?"),
        help_text=_("""
            Indicates that this skill is magical.
            """),
        default=False
    )
    capstone_flag = models.BooleanField(
        _("Is this a capstone?"),
        help_text=_("""
            Indicates that this is a capstone granted when
            requirements are met.
            (like for weapon skills)
            """),
        default=False
    )

    class Meta:
        ordering = ['cost', 'skill__name']

    def __str__(self):
        return "{header}:{skill}[{cost}]".format(
            header=self.header,
            skill=self.skill,
            cost=self.cost
        )
