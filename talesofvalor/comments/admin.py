"""Back end set up for Comments."""
from django.contrib import admin

from talesofvalor.comments.models import Comment

class CommentAdmin(admin.ModelAdmin):
    """Access the Comment from the admin."""
    pass

# Register the admin models
admin.site.register(Comment, CommentAdmin)