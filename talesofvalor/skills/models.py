"""
Skills and abilities that characters can use.

Characters have different things that they can do.

These skills have a cost to the character.

The costs can be changed or removed throught certain rules.

Skills may also come under "Headers" that must be purchased before
they can purchase the skills that belong to that header.
"""
from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField


class Header(models.Model):
    created = models.DateTimeField('date published', auto_now_add=True, editable=False)
    modified = models.DateTimeField('last updated', auto_now=True, editable=False)
    created_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_author', null=True)
    modified_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_updater', null=True)


class Skill(models.Model):
    created = models.DateTimeField('date published', auto_now_add=True, editable=False)
    modified = models.DateTimeField('last updated', auto_now=True, editable=False)
    created_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_author', null=True)
    modified_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_updater', null=True)

class SkillHeader(models.Model):