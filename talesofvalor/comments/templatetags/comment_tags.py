"""
Template tags used for comments to allow them to be used in multiple places 
easily.
"""
from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template

from ..models import Comment

register = template.Library()
t = get_template("comments/includes/comment_list.html")


@register.inclusion_tag(t)
def comments_display(obj):
    obj_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=obj_type, object_id=obj.id)
    print(f"COMMENTS:{comments}")
    return {
        'object': obj,
        'comments': comments
    }
