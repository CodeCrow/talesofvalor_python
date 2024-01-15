"""
Comment views.
"""
from rest_framework import viewsets
from rest_framework.permissions import BasePermission

from .models import Comment
from .serializers import CommentSerializer


class CanComment(BasePermission):
    """
    The current user is staff or owns the that is being manipulated.
    """
    message = "You don't own this character"

    def has_object_permission(self, request, view, obj):
        if self.request.user.has_perm('comments.add_comment'):
            return True
        return False


class CommentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (CanComment,)
        