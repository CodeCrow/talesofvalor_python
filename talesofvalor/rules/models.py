"""
Describes special rules for skills, headers, origins.

.
"""
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _

from djangocms_text_ckeditor.fields import HTMLField

from filer.fields.image import FilerImageField

from talesofvalor.origins.models import Origin
from talesofvalor.skills.models import Header, Skill

class Rule(models.Model):
    """
    Rules that change what skills/headers cost.

    Origins or other attributes may change what a skill costs.

    Rules track those changes and should be run when adding up
    character point changes/totals.

    Grant skills are skills that have the Boolean "free" field set to true:  Then they fulfill the requirement, 
    they get the skill automatically without having to buy it.
    """

    SKILL_RULE = 'SkillRule'
    HEADER_RULE = 'HeaderRule'
    ORIGIN_RULE = 'OriginRule'
    GRANT_RULE = 'GrantRule' # happens without having to purchase the skill:  The skill is given automatically.
    RULE_REQUIREMENT_CHOICES = (
        (SKILL_RULE, 'Skill Rule'),
        (HEADER_RULE, 'Header Rule'),
        (ORIGIN_RULE, 'Origin Rule'),
        (GRANT_RULE, 'Grant Rule')
    )
    name = models.CharField(max_length=100)
    description = HTMLField(blank=False)
    # the origin, header, skill, grant that invokes this rule.
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(
            app_label='origins', model='Origin'
        ) | models.Q(
            app_label='skills', model='Header'
        ) | models.Q(
            app_label='skills', model='Skill'
        )

    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # the skill that this will effect
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    # the new cost of the skill
    new_cost = models.PositiveIntegerField(default=0)
    # The character just gets this skill for free, without having to buy it at all.
    free = models.BooleanField(default=False, help_text=_("This is granted for free if the requirements are met."))
    # There are a limited number of times that the user can choose this skill as a result of fulfilling
    # The requirement.  Defaults to infinite.
    picks_remaining = models.PositiveIntegerField(null=True, blank=True)

    def __unicode__(self):
        """General display of model."""
        return "{}".format(
            self.name
        )

    @property
    def type(self):
        if self.free:
            return self.GRANT_RULE
        return "{} Rule".format(self.content_type.name.capitalize())
