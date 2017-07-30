"""
Describes special rules for skills, headers, origins.

.
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from filer.fields.image import FilerImageField

from talesofvalor.origins.models import Origin
from talesofvalor.skills.models import Header, Skill

class Rules(models.Model):
    """
    Rules that change what skills/headers cost.

    Origins or other attributes may change what a skill costs.

    Rules track those changes and should be run when adding up
    character point changes/totals.
    """

    SKILL_RULE = 'SkillRule'
    HEADER_RULE = 'HeaderRule'
    ORIGIN_RULE = 'OriginRule'
    GRANT_RULE = 'GrantRule'
    RULE_REQUIREMENT_CHOICES = (
        (SKILL_RULE, 'Skill Rule'),
        (HEADER_RULE, 'Header Rule'),
        (ORIGIN_RULE, 'Origin Rule'),
        (GRANT_RULE, 'Grant Rule')
    )

    SKILL_CHANGE = 'SkillChange'
    HEADER_CHANGE = 'HeaderChange'
    type = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SkillGrant'
    )
    # the origin, header, grant that invokes this rule.
    # TODO: Replace this with a contenttype
    requirement_id = models.PositiveIntegerField()
    # the resulting change in cost
    change_type = models.CharField(
        max_length=20,
        choices=RULE_REQUIREMENT_CHOICES,
        default='SkillGrant'
    )
    result_id = models.PositiveIntegerField(Skill)
    new_cost = models.PositiveIntegerField(default=0)
    free = models.BooleanField(default=False)
    picks_remaining = models.PositiveIntegerField(default=10000)
