"""
Comment views.
"""
from django.contrib.auth.models import User

from rest_framework import status, viewsets
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

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

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        # Add the author.
        data['created_by'] = data['modified_by'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data
        response_data['created_by'] = User.objects.get(pk=serializer.data['created_by']).username
        return Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers
        )
