"""
Comments that can be associated with different items.

Using https://docs.djangoproject.com/en/1.10/ref/contrib/contenttypes/#django.contrib.contenttypes.models.ContentType
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from djangocms_text_ckeditor.fields import HTMLField


class Comment(models.Model):
    subject = models.CharField(max_length=255, blank=False)
    comment = HTMLField(blank=False)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(
            app_label='characters', model='Character'
        ) | models.Q(
            app_label='events', model='Event'
        ) | models.Q(
            app_label='attendance', model='Attendance'
        ) | models.Q(
            app_label='betweengameabilities', model='betweengameability'
        ) | models.Q(
            app_label='origins', model='Origin'
        ) | models.Q(
            app_label='players', model='Player'
        ) | models.Q(
            app_label='skills', model='Header'
        ) | models.Q(
            app_label='skills', model='Skill'
        )

    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created = models.DateTimeField('date published', auto_now_add=True, editable=False)
    modified = models.DateTimeField('last updated', auto_now=True, editable=False)
    created_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_author', null=True, on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(User, editable=False, related_name='%(app_label)s_%(class)s_updater', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ('created', )
