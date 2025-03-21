"""
Template tags used for comments to allow them to be used in multiple places 
easily.
"""
from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from rest_framework.reverse import reverse
# from django.urls import reverse

from ..models import Comment

register = template.Library()
t = get_template("comments/includes/comment_list.html")


@register.inclusion_tag(t)
def comments_display(obj):
    obj_type = ContentType.objects.get_for_model(obj).model
    comments = Comment.objects.filter(content_type__model=obj_type, object_id=obj.id)
    return {
        'object': obj,
        'comments': comments,
        'object_type': obj_type
    }


@register.simple_tag
def comment_add():
    """
    Write out the javascript that creates a for for a new Comment
    and then sends out the form submission.
    """
    comment_url = reverse("comments:comment-list")
    add_script = f"""$('.add-comment').click((e)=>{{
        let $addButton = $(e.currentTarget);
        let objectId = $(e.currentTarget).data('objectid');
        let objectType = $(e.currentTarget).data('objecttype');
        let $comment_form = $('<form>');
        $comment_form.append($('<h5>Add a Comment:</h5>'));
        $comment_form.append($('<textarea name="comment">'));
        $comment_form.append($('<br>'));
        $comment_form.append($('<input type="hidden" id="object_id" name="object_id" value="' + objectId + '">'));
        $comment_form.append($('<input type="hidden" name="content_type" value="' + objectType + '">'));
        $comment_form.append($('<input type="button" value="save" class="submit-comment btn btn-primary">'));

        $('#controls_comment_' + objectId).append($comment_form);

        $addButton.hide();
    }});
    $('.controls-comment').on('click', '.submit-comment', (e) => {{
        let $comment_form = $(e.currentTarget).parent('form');
        let serialized_data = $comment_form.serialize();
        var objectId = $comment_form.children('#object_id').val();
        var $commentList = $('#controls_comment_' + objectId);
        // turn off the form
        var $inputs = $comment_form.find("input, select, button, textarea");
        $inputs.prop('disabled', true);
        var request = $.post("{comment_url}", serialized_data, (e) => {{
            $addButton = $commentList.children('.add-comment');
            $comment_form.remove();
            comment_display(e, '#controls_comment_' + objectId);
            $commentList.append($addButton.show());

        }})
        .fail((response)=>{{
            if (response.status == 400) {{
                var errorString = '';
                Object.keys(response.responseJSON).forEach(function(key, index) {{
                    errorString += key + ": " +  response.responseJSON[key] + "<br />";
                }});
                showError("Error Creating Comment", errorString);
            }} else {{
                showError("Error Creating Comment", response.responseText);
            }}
        }})
        .always(()=>{{
            $inputs.prop('disabled', false);
        }});
    }});

    var comment_display = (comment, dom_selector)=> {{
        let $node = $(dom_selector);
        console.log(dom_selector);
        console.log($node);
        console.log(comment);
        let comment_string = '<li class="comment"><p><h4>' + comment.created_by + ' - ' + comment.created  + '</h4>' + comment.comment + '</p></li>'
        $node.append(comment_string);
    }}
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


@register.simple_tag
def comment_list(obj):
    """
    JavaScript to write out a list of comments.
    """
    obj_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=obj_type, object_id=obj.id)
    return {
        'object': obj,
        'comments': comments
    }
    list_script = f"""
    """

    return mark_safe(list_script)