"""
Template tags used for comments to allow them to be used in multiple places 
easily.
"""
from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from ..models import Comment

register = template.Library()
t = get_template("comments/includes/comment_list.html")


@register.inclusion_tag(t)
def comments_display(obj):
    obj_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=obj_type, object_id=obj.id)
    return {
        'object': obj,
        'comments': comments
    }


@register.simple_tag
def comment_add():
    """
    Write out the javascript that creates a for for a new Comment
    and then sends out the form submission.
    """
    add_script = """
    $('.add-comment').click((e)=>{
        let objectId = $(e.currentTarget).data('objectid');
        console.log($(e.currentTarget).data('objectid'));
        $comment_form = $('<form>');
        $comment_form.append($('<h5>Add a Comment:</h5>'));
        $comment_form.append($('<textarea>'));
        $comment_form.append($('<br>'));
        $comment_form.append($('<input type="button" value="save" class="submit-comment btn btn-primary">'));
        console.log($comment_form);
        console.log($('#controls_comment_' + objectId));
        $('#controls_comment_' + objectId).append($comment_form);
        $(e.currentTarget).remove();
    });
    """
    return mark_safe(add_script)


@register.simple_tag
def comment_delete():
    """
    Write out the javascript that deletes a comment..
    """
    delete_script = """
    """
    return mark_safe(delete_script)
