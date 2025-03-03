"""Back end set up for Comments."""
from django.contrib import admin

from talesofvalor.comments.models import Comment


class CommentAdmin(admin.ModelAdmin):
    """Access the Comment from the admin."""
    list_display = ("comment", "created_by", )
    readonly_fields = ("created_by", "modified_by")


# Register the admin models
admin.site.register(Comment, CommentAdmin)